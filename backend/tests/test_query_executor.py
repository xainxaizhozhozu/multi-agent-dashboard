"""
Tests for services.query_executor.QueryExecutor
"""

import os
import sqlite3
import pytest

from services.query_executor import QueryExecutor


@pytest.fixture()
def executor(temp_db):
    qe = QueryExecutor()
    qe.db_path = temp_db
    return qe


class TestValidSelects:

    def test_simple_select_all(self, executor):
        result = executor.execute("SELECT * FROM sales")
        assert "error" not in result
        assert result["row_count"] == 5
        assert set(result["columns"]) >= {"id", "date", "amount", "region"}

    def test_select_with_where(self, executor):
        result = executor.execute(
            "SELECT id, amount FROM sales WHERE region = '\u534e\u4e1c'"
        )
        assert "error" not in result
        assert result["row_count"] == 2

    def test_select_aggregation(self, executor):
        sql = (
            "SELECT region, SUM(amount) AS total "
            "FROM sales GROUP BY region ORDER BY total DESC"
        )
        result = executor.execute(sql)
        assert "error" not in result
        assert result["row_count"] == 3
        assert result["rows"][0][1] >= result["rows"][-1][1]

    def test_select_with_filter(self, executor):
        sql = "SELECT e.name, e.department FROM employees e WHERE e.status = 'active'"
        result = executor.execute(sql)
        assert "error" not in result
        assert result["row_count"] == 2

    def test_select_count(self, executor):
        result = executor.execute("SELECT COUNT(*) AS cnt FROM employees")
        assert "error" not in result
        assert result["rows"][0][0] == 3

    def test_select_with_order_and_limit(self, executor):
        sql = "SELECT amount FROM sales ORDER BY amount DESC LIMIT 2"
        result = executor.execute(sql)
        assert "error" not in result
        assert result["row_count"] == 2
        assert result["rows"][0][0] >= result["rows"][1][0]

    def test_select_substring_of_column(self, executor):
        sql = "SELECT SUBSTR(date, 1, 7) AS month FROM sales"
        result = executor.execute(sql)
        assert "error" not in result
        assert all(len(r[0]) == 7 for r in result["rows"])


class TestCTEQueries:

    def test_with_simple_cte(self, executor):
        sql = (
            "WITH top_sales AS ("
            "  SELECT region, amount FROM sales WHERE amount > 1000"
            ") SELECT * FROM top_sales"
        )
        result = executor.execute(sql)
        assert "error" not in result
        assert result["row_count"] >= 1
        for row in result["rows"]:
            assert row[1] > 1000

    def test_with_multiple_ctes(self, executor):
        sql = (
            "WITH "
            "vip AS (SELECT * FROM sales WHERE customer_type = 'VIP'), "
            "totals AS (SELECT region, SUM(amount) AS s FROM vip GROUP BY region) "
            "SELECT * FROM totals ORDER BY s DESC"
        )
        result = executor.execute(sql)
        assert "error" not in result
        assert result["row_count"] >= 1


class TestNonSelectRejected:

    @pytest.mark.parametrize("sql", [
        "INSERT INTO sales VALUES (99, '2026-01-01', 100, 'X', 'Y', 1, 'Z')",
        "UPDATE sales SET amount = 0 WHERE id = 1",
        "DELETE FROM sales WHERE id = 1",
        "DROP TABLE sales",
        "ALTER TABLE sales ADD COLUMN foo TEXT",
        "CREATE TABLE foo (id INTEGER)",
    ])
    def test_dml_ddl_rejected(self, executor, sql):
        result = executor.execute(sql)
        assert "error" in result
        conn = sqlite3.connect(executor.db_path)
        count = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
        conn.close()
        assert count == 5, "Database must not be modified"


class TestSemicolonBlocked:

    def test_select_then_drop(self, executor):
        result = executor.execute("SELECT 1; DROP TABLE sales")
        assert "error" in result

    def test_trailing_semicolon(self, executor):
        result = executor.execute("SELECT 1;")
        assert "error" in result

    def test_semicolon_in_comment_still_blocked(self, executor):
        result = executor.execute("SELECT 1 -- comment;")
        assert "error" in result


class TestAttachDetachBlocked:

    def test_attach_blocked(self, executor):
        result = executor.execute("ATTACH DATABASE '/tmp/evil.db' AS evil")
        assert "error" in result

    def test_detach_blocked(self, executor):
        result = executor.execute("DETACH DATABASE main")
        assert "error" in result


class TestPragmaBlocked:

    def test_pragma_write_blocked(self, executor):
        result = executor.execute("PRAGMA journal_mode = WAL")
        assert "error" in result

    def test_pragma_read_allowed_by_validator(self, executor):
        result = executor.execute("PRAGMA table_info(sales)")
        if "error" in result:
            assert "\u4e0d\u5141\u8bb8" not in result["error"]


class TestEmptySQL:

    @pytest.mark.parametrize("sql", ["", "   ", "\t\n  "])
    def test_empty_sql_rejected(self, executor, sql):
        result = executor.execute(sql)
        assert "error" in result


class TestRowLimit:

    def test_row_limit_respected(self, executor):
        conn = sqlite3.connect(executor.db_path)
        conn.execute("CREATE TABLE big_table (id INTEGER)")
        conn.executemany(
            "INSERT INTO big_table VALUES (?)",
            [(i,) for i in range(1100)],
        )
        conn.commit()
        conn.close()
        result = executor.execute("SELECT * FROM big_table")
        assert "error" not in result
        assert result["row_count"] == 1000


class TestConnectionCleanup:

    def test_connection_closed_after_success(self, executor):
        executor.execute("SELECT * FROM sales")
        conn = sqlite3.connect(executor.db_path)
        conn.execute("CREATE TABLE cleanup_test (id INTEGER)")
        conn.commit()
        conn.close()

    def test_connection_closed_after_error(self, executor):
        executor.execute("SELECT * FROM nonexistent_table_xyz")
        conn = sqlite3.connect(executor.db_path)
        conn.execute("CREATE TABLE cleanup_test2 (id INTEGER)")
        conn.commit()
        conn.close()


class TestInvalidSQL:

    def test_syntax_error(self, executor):
        result = executor.execute("SELECTT * FORM sales")
        assert "error" in result

    def test_nonexistent_table(self, executor):
        result = executor.execute("SELECT * FROM this_table_does_not_exist")
        assert "error" in result

    def test_invalid_column(self, executor):
        result = executor.execute("SELECT bogus_column FROM sales")
        assert "error" in result


class TestReadOnlyEngineLayer:

    def test_insert_fails_in_readonly_mode(self, temp_db):
        conn = sqlite3.connect(
            "file:{}?mode=ro".format(temp_db), uri=True
        )
        with pytest.raises(sqlite3.OperationalError):
            conn.execute(
                "INSERT INTO sales VALUES (99, '2026-01-01', 0, 'X', 'Y', 0, 'Z')"
            )
        conn.close()

    def test_case_insensitive_keyword_detection(self, executor):
        result = executor.execute(
            "insert INTO sales VALUES (99,'x',0,'x','x',0,'x')"
        )
        assert "error" in result

    def test_select_with_safe_alias(self, executor):
        sql = "SELECT amount AS latest_value FROM sales LIMIT 1"
        result = executor.execute(sql)
        assert "error" not in result

    def test_select_column_containing_update_substring(self, executor):
        conn = sqlite3.connect(executor.db_path)
        conn.execute("CREATE TABLE logs (id INTEGER, last_updated TEXT)")
        conn.execute("INSERT INTO logs VALUES (1, '2026-01-01')")
        conn.commit()
        conn.close()
        result = executor.execute("SELECT last_updated FROM logs")
        assert "error" not in result
        assert result["row_count"] == 1

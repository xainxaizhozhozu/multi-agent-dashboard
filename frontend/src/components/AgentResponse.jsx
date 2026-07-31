import { useState } from 'react'
import AgentChart from './AgentChart'

export default function AgentResponse({ result }) {
  const [showSql, setShowSql] = useState(false)

  if (!result.success) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
        {result.response_text || '分析失败，请重试'}
      </div>
    )
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
      <div className="flex items-center gap-2 mb-3">
        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
          {result.chart_type?.toUpperCase()}
        </span>
        <span className="text-xs text-gray-400">耗时 {result.elapsed_seconds}s</span>
        {result.review_passed && (
          <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">✓ 审查通过</span>
        )}
      </div>

      <p className="text-sm text-gray-600 mb-2">{result.explanation}</p>

      <AgentChart result={result} />

      {/* 数据表格 */}
      {result.raw_data && result.raw_data.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-gray-50">
                {result.columns?.map((col, i) => (
                  <th key={i} className="px-3 py-2 text-left font-medium text-gray-600 border-b">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.raw_data.slice(0, 8).map((row, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  {(Array.isArray(row) ? row : result.columns.map(c => row[c])).map((cell, j) => (
                    <td key={j} className="px-3 py-1.5 border-b border-gray-100 text-gray-700">
                      {typeof cell === 'number' ? cell.toLocaleString() : cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* SQL 展开 */}
      {result.sql && (
        <div className="mt-3">
          <button onClick={() => setShowSql(!showSql)} className="text-xs text-blue-500 hover:underline">
            {showSql ? '隐藏 SQL' : '查看 SQL'}
          </button>
          {showSql && (
            <pre className="mt-2 bg-gray-900 text-green-400 text-xs p-3 rounded-lg overflow-x-auto">{result.sql}</pre>
          )}
        </div>
      )}

      {/* Agent 时间线 */}
      {result.agent_timeline && (
        <div className="mt-3 flex gap-3 text-xs text-gray-400 flex-wrap">
          {Object.entries(result.agent_timeline).map(([agent, status]) => (
            <span key={agent} className="bg-gray-100 px-2 py-1 rounded">{agent}: {status}</span>
          ))}
        </div>
      )}
    </div>
  )
}

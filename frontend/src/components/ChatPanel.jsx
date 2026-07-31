import { useState } from 'react'
import { PieChart as PieIcon, Send } from 'lucide-react'
import AgentResponse from './AgentResponse'
import { agentApi } from '../api'

const SUGGESTIONS = [
  '各地区销售额对比',
  '客户类型消费占比',
  '产品类别 TOP5 排名',
  '月度销售趋势',
  '各部门平均薪资',
]

export default function ChatPanel() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async (query) => {
    query = (query || input).trim()
    if (!query || loading) return
    setInput('')
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: query }])
    setLoading(true)
    try {
      const result = await agentApi.chat(query)
      setMessages(prev => [...prev, { id: Date.now(), role: 'agent', result }])
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now(), role: 'agent',
        result: { success: false, response_text: err.message || '请求失败' }
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-100 flex items-center gap-2">
        <PieIcon size={18} className="text-blue-600" />
        <h3 className="text-sm font-semibold text-gray-700">AI 数据分析助手</h3>
        <span className="text-xs text-gray-400 ml-2">支持自然语言查询，自动生成图表</span>
      </div>

      {/* 推荐问题 */}
      <div className="px-5 py-3 flex flex-wrap gap-2 border-b border-gray-50">
        {SUGGESTIONS.map((s, i) => (
          <button key={i} onClick={() => handleSend(s)}
            className="px-3 py-1.5 bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-xs text-gray-600 rounded-full transition">
            {s}
          </button>
        ))}
      </div>

      {/* 消息列表 */}
      <div className="px-5 py-4 space-y-4 max-h-[500px] overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-center text-gray-400 text-sm py-8">输入问题或点击上方推荐，AI 将自动分析并生成图表</p>
        )}
        {messages.map((msg, i) => (
          <div key={msg.id || i}>
            {msg.role === 'user' ? (
              <div className="flex justify-end">
                <div className="bg-blue-600 text-white px-4 py-2 rounded-xl rounded-br-sm text-sm max-w-[70%]">{msg.content}</div>
              </div>
            ) : (
              <AgentResponse result={msg.result} />
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
            Agent 协作分析中...
          </div>
        )}
      </div>

      {/* 输入框 */}
      <div className="px-5 py-4 border-t border-gray-100">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="例如：各地区销售额对比、客户类型占比、月度趋势..."
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
          <button onClick={() => handleSend()} disabled={loading}
            className="px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2">
            <Send size={16} />
            分析
          </button>
        </div>
      </div>
    </div>
  )
}

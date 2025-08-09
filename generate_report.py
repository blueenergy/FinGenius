import re
from collections import defaultdict

def parse_final_votes(log_text):
    # 提取最终投票结果
    final_vote_pattern = re.compile(r"Final vote results: ({.*?}) \(total votes: (\d+)\)", re.DOTALL)
    m = final_vote_pattern.findall(log_text)
    if m:
        last_vote = m[-1]
        vote_dict = eval(last_vote[0])
        total_votes = int(last_vote[1])
        return vote_dict, total_votes
    return {}, 0

def parse_agent_votes(log_text):
    # 提取每位agent的最终投票和观点
    agent_vote_pattern = re.compile(r"([a-z_]+_agent)\[(bullish|bearish)\]: (.+?)(?=\n\d{4}-\d{2}-\d{2}|\Z)", re.DOTALL)
    agent_votes = agent_vote_pattern.findall(log_text)
    # 只保留最后一次观点
    agent_latest = {}
    for agent, vote, speak in agent_votes:
        agent_latest[agent] = (vote, speak.strip())
    return agent_latest

def parse_token_usage(log_text):
    # 提取token用量
    token_pattern = re.compile(r"Token usage: Input=(\d+), Cumulative Input=(\d+)")
    tokens = token_pattern.findall(log_text)
    if tokens:
        last = tokens[-1]
        return int(last[0]), int(last[1])
    return None, None

def parse_analysis_chain(log_text):
    # 提取分析链（每个agent的分析流程）
    chain = []
    agent_step_pattern = re.compile(r"Starting analysis with ([a-z_]+_agent) \((\d+)/6\)")
    for m in agent_step_pattern.findall(log_text):
        chain.append(m[0])
    return chain

def build_html_report(vote_dict, total_votes, agent_latest, token_input, token_cum, chain):
    agent_names = {
        "sentiment_agent": "市场情绪分析师",
        "risk_control_agent": "风险控制专家",
        "hot_money_agent": "游资分析师",
        "technical_analysis_agent": "技术分析师",
        "chip_analysis_agent": "筹码分析师",
        "big_deal_analysis_agent": "大单分析师"
    }
    # 结论
    bullish = vote_dict.get('bullish', 0)
    bearish = vote_dict.get('bearish', 0)
    if bullish > bearish:
        conclusion = '<span class="vote-bullish">最终结论：看涨，建议关注机会</span>'
    elif bullish < bearish:
        conclusion = '<span class="vote-bearish">最终结论：看跌，建议谨慎</span>'
    else:
        conclusion = '<span class="text-warning">最终结论：多空均衡，建议观望</span>'

    # HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>AI多专家分析报告</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {{ background: #f8f9fa; }}
    .logic-step {{ border-left: 4px solid #4a6bdf; margin-bottom: 2rem; padding-left: 1rem; background: #fff; border-radius: 0.5rem; box-shadow: 0 2px 8px #eee; }}
    .agent-title {{ font-weight: bold; color: #4a6bdf; }}
    .vote-bullish {{ color: #28a745; font-weight: bold; }}
    .vote-bearish {{ color: #dc3545; font-weight: bold; }}
    .debate-block {{ background: #f6f8fa; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; }}
    .final-result {{ font-size: 1.3rem; font-weight: bold; }}
    .timeline {{ border-left: 2px solid #dee2e6; margin-left: 1rem; padding-left: 1.5rem; }}
    .timeline-step {{ margin-bottom: 1.5rem; }}
    .timeline-step .badge {{ font-size: 1rem; }}
    .highlight {{ background: #e3f2fd; border-radius: 0.3rem; padding: 0.5rem; }}
  </style>
</head>
<body>
<div class="container my-4">
  <h1 class="mb-3">AI多专家分析报告</h1>
  <p class="text-muted">分析时间：自动生成</p>

  <div class="logic-step">
    <h2>一、分析流程与逻辑链</h2>
    <div class="timeline">
"""
    for idx, agent in enumerate(chain, 1):
        agent_cn = agent_names.get(agent, agent)
        html += f"""      <div class="timeline-step">
        <span class="badge bg-primary">Step {idx}</span>
        <span class="agent-title">{agent_cn}</span>
      </div>
"""
    html += """    </div>
  </div>
  <div class="logic-step">
    <h2>二、专家辩论与观点溯源</h2>
"""
    for agent, (vote, speak) in agent_latest.items():
        agent_cn = agent_names.get(agent, agent)
        vote_str = '<span class="vote-bullish">[看涨]</span>' if vote == 'bullish' else '<span class="vote-bearish">[看跌]</span>'
        html += f"""    <div class="debate-block">
      <b>{agent_cn}{vote_str}：</b> {speak}
    </div>
"""
    html += f"""  </div>
  <div class="logic-step">
    <h2>三、最终投票与结论</h2>
    <div class="mb-3">
      <span class="vote-bullish">看涨票数：{bullish}</span> &nbsp; | &nbsp; <span class="vote-bearish">看跌票数：{bearish}</span>
    </div>
    <div class="final-result">
      {conclusion}
    </div>
    <p class="text-muted small">（{total_votes}位专家参与投票）</p>
  </div>
  <div class="logic-step">
    <h2>四、AI分析流程日志摘要</h2>
    <ul>
      <li>Token用量：输入{token_input}，累计{token_cum}</li>
      <li>分析流程：{' → '.join([agent_names.get(a, a) for a in chain])}</li>
      <li>最终投票：看涨{bullish}，看跌{bearish}</li>
    </ul>
  </div>
  <footer class="text-center text-muted mt-5 mb-3 small">
    &copy; 2025 FinGenius AI分析系统 | 本报告由AI自动生成，仅供参考，不构成投资建议。
  </footer>
</div>
</body>
</html>
"""
    return html

def main(log_path, output_html):
    with open(log_path, encoding='utf-8') as f:
        log_text = f.read()
    vote_dict, total_votes = parse_final_votes(log_text)
    agent_latest = parse_agent_votes(log_text)
    token_input, token_cum = parse_token_usage(log_text)
    chain = parse_analysis_chain(log_text)
    html = build_html_report(vote_dict, total_votes, agent_latest, token_input, token_cum, chain)
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"报告已生成：{output_html}")

# 用法示例
if __name__ == "__main__":
    main("logs/20250804085556.log", "logs/auto_report.html")
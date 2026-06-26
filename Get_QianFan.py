# Get_QianFan.py
import json
from openai import OpenAI
from config import Config

def getQianFan(air_quality_data):
    try:
        # 解析传入的空气质量JSON数据
        data = json.loads(air_quality_data)
    except json.JSONDecodeError as e:
        return {"response": f"数据解析失败:{str(e)}"}

    # 初始化千帆客户端
    client = OpenAI(
        base_url='https://qianfan.baidubce.com/v2',
        api_key=Config.API_KEY,
        # 这里把APP_ID注释掉了，新版不需要，不影响调用
        # default_headers={"appid": Config.APP_ID}
    )

    system_prompt = """
你是一个专业的空气质量数据分析与预测系统。请根据提供的JSON格式的空气质量数据进行分析：
1. 总结过去一个月的空气质量趋势（AQI、PM2.5等关键指标）。
2. 预测未来3天的空气质量（基于历史规律）。
3. 提供改善空气质量的建议（如减少外出、佩戴口罩等）。
请注意：
- 使用纯文本格式，不要使用Markdown符号（如#、*等）
- 用中文回答，分点列出关键结论
- 对PM2.5和AQI进行重点分析
- 给出可操作的改善建议
- 不要使用任何Markdown格式符号
    """

    # 把数据传给模型
    user_prompt = f"以下是空气质量数据：{json.dumps(data, ensure_ascii=False)}"

    # 调用DeepSeek模型（替换了原来的ernie-lite-8k）
    response = client.chat.completions.create(
        model="deepseek-v3.1-250821",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.95,
        top_p=0.7,
        extra_body={
            "penalty_score": 1
        }
    )

    # 提取模型返回的文本内容
    clean_response = response.choices[0].message.content
    return {"response": clean_response}
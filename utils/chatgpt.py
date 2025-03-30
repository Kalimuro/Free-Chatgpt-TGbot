from g4f.client import Client

client = Client()


async def get_gpt_otvet(user_message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}],
            web_search=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        return "К сожалению, не удалось получить ответ от GPT. Продублируйте свой вопрос, или задайте новый"





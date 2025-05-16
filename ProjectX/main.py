import ollama

def stream_chat(prompt, model='llama3.2'):
    response = ollama.chat(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        stream=True
    )

    print("Assistant: ", end='', flush=True)
    for chunk in response:
        print(chunk['message']['content'], end='', flush=True)

if __name__ == "__main__":
    user_input = input("You: ")
    stream_chat(user_input)

def render_prompt(history, question, lang="en"):
    lines = []
    for h in history:
        if lang == "de":
            lines.append(f"Frage: {h['question']}")
            lines.append(f"Antwort: {h['answer']}")
        else:
            lines.append(f"Question: {h['question']}")
            lines.append(f"Answer: {h['answer']}")
        lines.append("---")

    if lang == "de":
        lines.append(f"Frage: {question}")
        lines.append("Bitte antworte klar, professionell und auf Deutsch.")
    else:
        lines.append(f"Question: {question}")
        lines.append("Please reply clearly, professionally, and in English.")

    return "\n".join(lines)

"""
app.py - Gradio web interface for the UNC Unofficial Guide RAG system
Run with: python app.py
Then open http://localhost:7860
"""

import gradio as gr
from query import ask


def handle_query(question: str) -> tuple[str, str, str]:
    """
    Gradio handler: takes a question string, returns (answer, sources, chunks_display).
    """
    if not question or not question.strip():
        return "Please enter a question.", "", ""

    result = ask(question.strip())

    answer = result["answer"]

    sources_text = "\n".join(f"• {s}" for s in result["sources"])

    # Format retrieved chunks for display
    chunks_lines = []
    for i, chunk in enumerate(result["chunks"], 1):
        chunks_lines.append(
            f"[{i}] {chunk['source']} (distance: {chunk['distance']:.4f})\n"
            f"{chunk['text'][:300]}{'...' if len(chunk['text']) > 300 else ''}"
        )
    chunks_text = "\n\n".join(chunks_lines)

    return answer, sources_text, chunks_text


# ─── Build the Gradio UI ──────────────────────────────────────────────────────

with gr.Blocks(title="UNC Unofficial Guide", theme=gr.themes.Soft()) as demo:

    gr.Markdown(
        """
        # 🐏 UNC Unofficial Guide
        **The student knowledge your course catalog doesn't have.**
        Ask about professors, dining, housing, registration, careers, campus life, and more.
        All answers are grounded in real student reviews and posts — no hallucination.
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            question_box = gr.Textbox(
                label="Your question",
                placeholder='e.g. "How hard is COMP 401?" or "Which dining hall has the shortest lines?"',
                lines=2,
            )
            ask_btn = gr.Button("Ask the Guide", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown(
                """
                **Example questions:**
                - What are KMP's exams like in COMP 401?
                - Which dining hall is least crowded at lunch?
                - How does the UNC housing lottery work?
                - When should I apply for tech internships?
                - What's the best place to study besides Davis Library?
                - Is Greek life worth it at UNC?
                """
            )

    answer_box = gr.Textbox(
        label="Answer",
        lines=8,
        interactive=False,
    )

    with gr.Accordion("Sources", open=True):
        sources_box = gr.Textbox(
            label="Retrieved from",
            lines=4,
            interactive=False,
        )

    with gr.Accordion("Retrieved chunks (debug view)", open=False):
        chunks_box = gr.Textbox(
            label="Top chunks used to generate this answer",
            lines=12,
            interactive=False,
        )

    # Wire up button and Enter key
    ask_btn.click(
        fn=handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box, chunks_box],
    )
    question_box.submit(
        fn=handle_query,
        inputs=question_box,
        outputs=[answer_box, sources_box, chunks_box],
    )

    gr.Markdown(
        "_Answers are based solely on collected student reviews and posts. "
        "Always verify important decisions with official UNC sources._"
    )


if __name__ == "__main__":
    demo.launch()

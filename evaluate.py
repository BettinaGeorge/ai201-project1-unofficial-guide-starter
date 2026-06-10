"""
evaluate.py - Evaluation framework for the UNC Unofficial Guide RAG system

Runs 5 pre-defined test questions with ground-truth expected answers.
Prints a structured report suitable for copying into the README evaluation section.
Run AFTER embed.py has built the ChromaDB index.
"""

from query import ask

# ─── Test suite ───────────────────────────────────────────────────────────────

TEST_QUESTIONS = [
    {
        "id": 1,
        "question": "What are COMP 401 exams like and how should students prepare?",
        "expected": (
            "Exams are based almost entirely on the assignments. Understanding every line of code "
            "you wrote is the best preparation. Two midterms and a cumulative final. No curves. "
            "Study design patterns specifically."
        ),
    },
    {
        "id": 2,
        "question": "Is Kris Jordan a good professor for intro CS?",
        "expected": (
            "Yes — consistently rated highly (4.7/5). Known for making coding accessible to "
            "beginners, creative projects, clear instructions, and a well-run course. "
            "Good choice for students new to programming."
        ),
    },
    {
        "id": 3,
        "question": "What is COMP 530 Operating Systems like and is it worth taking?",
        "expected": (
            "A demanding course where students implement a real OS kernel in C over the semester. "
            "Hard but produces deep understanding of how computers work. Worth it for students "
            "interested in systems, embedded, or infrastructure roles. Take COMP 311 and 411 first."
        ),
    },
    {
        "id": 4,
        "question": "How difficult is COMP 421 Databases and what does it cover?",
        "expected": (
            "Manageable workload. Covers SQL, schema design, normalization, and transactions. "
            "Jeff Terrell teaches it clearly with live SQL demos. Assignments are realistic and "
            "skills transfer directly to internships."
        ),
    },
    {
        "id": 5,
        "question": "What do students say about Diane Pozefsky and COMP 523?",
        "expected": (
            "Pozefsky is described as direct and supportive, a legend in the department. "
            "COMP 523 is a real client software project spanning a full semester. Teaches Git "
            "workflow, standups, stakeholder communication, and demos. Considered one of the "
            "best courses in the CS major."
        ),
    },
]

# ─── Out-of-scope question (should trigger refusal) ───────────────────────────
OUT_OF_SCOPE = {
    "question": "What is the current tuition at UNC Chapel Hill for out-of-state students?",
    "expected_behavior": "System should say it does not have enough information on that topic.",
}


def run_evaluation() -> None:
    print("=" * 70)
    print("UNC UNOFFICIAL GUIDE — EVALUATION REPORT")
    print("=" * 70)

    for test in TEST_QUESTIONS:
        print(f"\n{'─'*70}")
        print(f"Question {test['id']}: {test['question']}")
        print(f"{'─'*70}")
        print(f"Expected answer (summary):\n  {test['expected']}\n")

        result = ask(test["question"])

        print(f"System answer:\n{result['answer']}\n")
        print(f"Retrieved sources: {', '.join(result['sources'])}")
        print(f"Retrieved chunks:")
        for i, chunk in enumerate(result["chunks"], 1):
            print(f"  [{i}] {chunk['source']} (dist={chunk['distance']:.4f}): "
                  f"{chunk['text'][:120]}...")
        print(f"\n[Accuracy judgment: fill in — accurate / partially accurate / inaccurate]")

    # Out-of-scope test
    print(f"\n{'─'*70}")
    print(f"OUT-OF-SCOPE QUERY TEST")
    print(f"{'─'*70}")
    print(f"Question: {OUT_OF_SCOPE['question']}")
    print(f"Expected behavior: {OUT_OF_SCOPE['expected_behavior']}\n")

    oos_result = ask(OUT_OF_SCOPE["question"])
    print(f"System response:\n{oos_result['answer']}")
    print(f"Sources: {', '.join(oos_result['sources']) if oos_result['sources'] else 'none'}")

    print(f"\n{'='*70}")
    print("Evaluation complete. Fill in accuracy judgments above for the README.")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()

from dotenv import load_dotenv
load_dotenv()

from backend.evaluation.evaluator import (
    exact_match,
    keyword_coverage,
    retrieval_hit_at_k,
    load_dataset
)
from backend.src.agent.agent import run_agent_with_debug


def main():
    dataset = load_dataset("backend/evaluation/dataset.json")
    total = len(dataset)
    retrieval_hit_score = 0
    exact_match_score = 0
    keyword_scores = []
    for item in dataset:
        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_keywords = item["expected_keywords"]
        expected_chunk_substring = item["expected_chunk_substring"]
        result = run_agent_with_debug(question)
        predicted_answer = result["answer"]
        retrieved_chunks = result["retrieved_chunks"]
        if retrieval_hit_at_k(retrieved_chunks, expected_chunk_substring):
            retrieval_hit_score += 1
        if exact_match(predicted_answer, expected_answer):
            exact_match_score += 1
        keyword_scores.append(keyword_coverage(predicted_answer, expected_keywords))
        print("\n---")
        print("Q:", question)
        print("Answer:", predicted_answer)
        print("Expected:", expected_answer)
        print("Retrieval Hit:", retrieval_hit_at_k(retrieved_chunks, expected_chunk_substring))

    print("\n===== SUMMARY =====")
    print(f"Total Questions: {total}")
    print(f"Retrieval Hit@k: {retrieval_hit_score / total:.2%}")
    print(f"Exact Match: {exact_match_score / total:.2%}")
    print(f"Avg Keyword Coverage: {sum(keyword_scores) / total:.2%}")

if __name__ == "__main__":
    main()

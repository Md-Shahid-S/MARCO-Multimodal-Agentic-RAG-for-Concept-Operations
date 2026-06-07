# ingestion/arxiv_daemon.py
import arxiv, time, os
from apscheduler.schedulers.blocking import BlockingScheduler
from ingestion.pdf_parser import extract_text_from_url
from ingestion.concept_extractor import extract_concepts
from knowledge_base.updater import update_index_with_new_concepts
from dotenv import load_dotenv

load_dotenv()

QUERY  = os.getenv("ARXIV_SEARCH_QUERY", "(\"DevOps\" OR \"DevSecOps\" OR \"CI/CD\" OR \"GitOps\") AND (\"microservice\" OR \"architecture\")")
MAX_R  = int(os.getenv("ARXIV_MAX_RESULTS", 5)) # Set to 5 for quick initial run
DELAY  = float(os.getenv("ARXIV_RATE_LIMIT_SECONDS", 3))

def fetch_new_papers(since_date: str) -> list[dict]:
    """Pull papers published after since_date."""
    # Since python 'arxiv' library requires arxiv.Client()
    client = arxiv.Client()
    search = arxiv.Search(
        query=QUERY,
        max_results=MAX_R,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    results = []
    for paper in client.results(search):
        if str(paper.published.date()) <= since_date:
            break
        results.append({
            "arxiv_id":   paper.entry_id.split("/")[-1],
            "title":      paper.title,
            "abstract":   paper.summary,
            "pdf_url":    paper.pdf_url,
            "published":  str(paper.published.date())
        })
        time.sleep(DELAY)
    return results

def weekly_ingestion_job():
    from ingestion.state import get_last_ingestion_date, set_last_ingestion_date
    last_date = get_last_ingestion_date()
    print(f"[arXiv daemon] Fetching papers since {last_date}")
    papers = fetch_new_papers(last_date)
    print(f"[arXiv daemon] Found {len(papers)} new papers")

    all_new_concepts = []
    for paper in papers:
        print(f"[arXiv daemon] Processing '{paper['title']}'")
        text = extract_text_from_url(paper["pdf_url"])
        if text:
            concepts = extract_concepts(text, paper)
            all_new_concepts.extend(concepts)

    if all_new_concepts:
        # Check drift before updating (optional but good for logs)
        try:
            from knowledge_base.drift_detector import compute_corpus_centroid, check_drift
            from knowledge_base.builder import INDEX_PATH
            if os.path.exists(INDEX_PATH):
                old_centroid = compute_corpus_centroid(INDEX_PATH)
                drift_info = check_drift(all_new_concepts, old_centroid, INDEX_PATH)
                print(f"[arXiv daemon] Drift shift: {drift_info['cosine_shift']}")
                if drift_info["drift_detected"]:
                    print(f"[arXiv daemon] {drift_info['alert_message']}")
        except Exception as e:
            print(f"[arXiv daemon] Drift check failed: {e}")

        update_index_with_new_concepts(all_new_concepts)
        print(f"[arXiv daemon] Added {len(all_new_concepts)} new concepts to index")
    else:
        print("[arXiv daemon] No new concepts extracted.")

    set_last_ingestion_date()

def start_daemon():
    scheduler = BlockingScheduler()
    scheduler.add_job(weekly_ingestion_job, "cron", day_of_week="mon", hour=2)
    scheduler.start()

if __name__ == "__main__":
    weekly_ingestion_job()   # Run once immediately for testing

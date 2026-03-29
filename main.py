import glob
import os
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DOC_GLOBS = ["docs/**/*.md", "docs/**/*.json"]
VECTOR_STORE_NAME = "Example Internal Markdown Docs"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def create_vector_store() -> str:
    vs = client.vector_stores.create(name=VECTOR_STORE_NAME)
    return vs.id

def upload_docs(vector_store_id: str):
    paths = []
    for pattern in DOC_GLOBS:
        paths.extend(glob.glob(pattern, recursive=True))
    if not paths:
        raise RuntimeError(f"No files found (globs={DOC_GLOBS}).")

    handles = [open(p, "rb") for p in paths]
    try:
        batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=handles,
        )
        # batch.status should be "completed" when ready
        return batch
    finally:
        for h in handles:
            h.close()

def ask(vector_store_id: str, question: str) -> str:
    resp = client.responses.create(
        model="gpt-4.1",
        input=question,
        tools=[{"type": "file_search", "vector_store_ids": [vector_store_id]}],
    )
    return resp.output_text

if __name__ == "__main__":
    import sys
    resync = "--resync" in sys.argv

    vs_id = os.environ.get("VECTOR_STORE_ID")

    if vs_id and not resync:
        print(f"Reusing existing vector store: {vs_id}")
        print("Run with --resync to delete existing files and re-upload.")
    else:
        if resync and vs_id:
            # Delete all existing files from the store before re-uploading
            existing = client.vector_stores.files.list(vector_store_id=vs_id)
            for f in existing.data:
                client.vector_stores.files.delete(vector_store_id=vs_id, file_id=f.id)
            print(f"Cleared existing files from vector store: {vs_id}")
        else:
            vs_id = create_vector_store()
            print(f"Vector store created: {vs_id}")
            print(f"Add this to your .env: VECTOR_STORE_ID={vs_id}")

        batch = upload_docs(vs_id)
        print("Upload batch status:", batch.status)

    q = "How do I assign the admin role to a user?"
    print("\nQ:", q)
    print("A:", ask(vs_id, q))
"""
Demonstrate how to upload a folder to the server and then summarize the contents of all files in the folder.
This mirrors a common transactional experience where exploratory diligence is performed on a large number of files
and then a summary of the contents is generated.
"""

# imports
import asyncio
import textwrap
from pathlib import Path

# kelvin clients
from kelvin.api.document_index.async_client import KelvinDocumentIndexAsyncClient
from kelvin.api.document_index.commands.load_folder import load_folder
from kelvin.api.nlp.async_client import KelvinNLPAsyncClient

async def main():
    # setup the clients
    doc_client = KelvinDocumentIndexAsyncClient()
    nlp_client = KelvinNLPAsyncClient()

     # upload the folder
    data_folder = Path(__file__).parent.parent / "data" / "bluth-sample/"
    await load_folder(data_folder, num_workers=4, progress=True)

    # summarize all documents
    summary_list = []
    documents = await doc_client.get_documents()
    for document in documents:
        # get document file instance
        file_instances = await doc_client.get_document_instances(document["id"])
        file_name = file_instances[0]['file_name']

        # summarize
        print(f"Summarizing: {file_name}")
        try:
            summary = await doc_client.get_document_summary(document["id"], engine="gpt-3.5-turbo")
            summary_list.append(f"Summary of {file_name}:\n{summary['summary']}")
            print(textwrap.fill(summary["summary"], 80))
        except Exception as e:
            print("No summary available for this document")

        print("=" * 80)

    # answer a specific question
    answer = await nlp_client.get_llm_answer(engine="gpt-3.5-turbo",
                                                       text="\n\n".join(summary_list),
                                                       question="Which files contain labor and employment materials?",
                                                       context_type="list of summaries from a deal room",
                                                       )
    print("Labor and Employment:")
    print(textwrap.fill(answer["answer"], 80))

    # answer a specific question
    answer = await nlp_client.get_llm_answer(engine="gpt-3.5-turbo",
                                             text="\n\n".join(summary_list),
                                             question="Which documents contain financial information?",
                                             context_type="list of summaries from a deal room",
                                             )
    print("Financial Docs:")
    print(textwrap.fill(answer["answer"], 80))

if __name__ == "__main__":
    asyncio.run(main())

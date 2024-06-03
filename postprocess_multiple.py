import sys, os
from openai import OpenAI

def main(argv):
    # handling errors
    if len(argv) != 2:
        print("usage: postprocess_multiple.py <PATH_OF_TRANSCRIPT>")
        exit()
        
    if(not os.path.exists(argv[1])):
       print("Transcript file not found")
       exit()

    try:
        with open("key.txt", mode="r") as key:
            OPENAI_API_KEY = key.read()
    except:
        print("api key not found")
        exit()
    
    subjects = ["typo3", "outline", "topic", "opinion", "decision"]
    insts = {}
    try:
        for subject in subjects:
            with open(f"./asst_inst/inst_{subject}.txt", mode="r", encoding="utf-8") as inst:
                insts[subject] = inst.read()
    except:
        print(f"instruction file for {subject} not found")
        exit()


    # create/retrieve assistant
    client = OpenAI(api_key=OPENAI_API_KEY)
    my_name = "kang" # assistant separator (Must be 4 letters for now)

    my_assistants = {}
    for assistant in client.beta.assistants.list():
        if (subject := assistant.name[5:]) in subjects:
            tmp = client.beta.assistants.retrieve(assistant.id)
            my_assistants[subject] = client.beta.assistants.update(
                assistant_id=tmp.id,
                instructions=insts[subject],
                temperature=0.01
                )
    for subject in set(subjects)-set(my_assistants):
        my_assistants[subject] = client.beta.assistants.create(
            model="gpt-4o",
            name=my_name+"_"+subject,
            description="transcript assistant",
            instructions=insts[subject],
            tools=[{"type":"file_search"}], 
            temperature=0.01
        )
    

    # upload file to retrieved/created vector store
    my_vector_store = None
    if my_vector_store is None:
        my_vector_store = client.beta.vector_stores.create(name=my_name,
                                                           expires_after={'anchor':'last_active_at',
                                                                          'days':1}
                                                            )
    original_file = client.beta.vector_stores.files.upload_and_poll(
        vector_store_id=my_vector_store.id,
        file=open(argv[1], "rb")
    )


    # create thread
    thread = client.beta.threads.create(
        messages=[
            {"role":"user",
             "content":f"Do your task as your instruction with '{argv[1]}'file"
            }
        ],
        tool_resources={"file_search":{"vector_store_ids": [my_vector_store.id]}}
    )
    


    # run
    for subject in subjects:
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=my_assistants[subject].id
        )
        messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
        message_content = messages[0].content[0].text
        print(message_content.value)
        if subject != "topic":
            with open(f"{argv[1][:-4]}_{subject}.txt",
                    mode="w",
                    encoding="utf-8") as output:
                output.write(message_content.value)
            if subject == "typo3":
                client.beta.vector_stores.files.delete(
                    vector_store_id=my_vector_store.id,
                    file_id=original_file.id
                )
                client.beta.vector_stores.files.upload_and_poll(
                    vector_store_id=my_vector_store.id,
                    file=open(f"{argv[1][:-4]}_typo3.txt", "rb")
                )
        if subject == subjects[-1]:
            break
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content="Do your task as your instruction considering previously extracted informations and attached file"
        )


if __name__ == "__main__":
    argv = sys.argv
    main(argv)
    # main(["asdf", "ex3.txt"])
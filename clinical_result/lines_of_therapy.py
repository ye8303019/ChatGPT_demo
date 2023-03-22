import utils.chunk_utils as cu
import utils.openai_utils as ou

token_threshold = 1800
model = "gpt-3.5-turbo"
meeting_abstract = cu.get_file_content("abstract_23", token_threshold, model)


# if only CTGov clinical trials could be listed in the abstract
def gpt_extraction(abstract):
    message = [{"role": "system", "content": "Now you are a excellent NLP Classification model"},
               {"role": "user", "content": """Now i need you to judge whether the content I give to you include 'Lines of Therapy'.  The lines of Therapy should only be 'First-line therapy', 'Second-line therapy', 'Third-line therapy', 'Salvage therapy', 'Maintenance therapy', 'Adjuvant therapy', 'Neoadjuvant therapy', 'Palliative therapy'. and here are the definitions:
First-line therapy: The first treatment given for a disease. It is often part of a standard set of treatments, such as surgery followed by chemotherapy and radiation. When used by itself, first-line therapy is the one accepted as the best treatment. If it doesn’t cure the disease or it causes severe side effects, other treatment may be added or used instead. Also called induction therapy, primary therapy, and primary treatment.

Second-line therapy: Treatment that is given when initial treatment (first-line therapy) doesn’t work, or stops working.

Third-line therapy: Treatment that is given when both initial treatment (first-line therapy) and subsequent treatment (second-line therapy) don’t work, or stop working.

Salvage therapy: Treatment that is given after the cancer has not responded to other treatments.

Maintenance therapy: Treatment that is given to help keep cancer from coming back after it has disappeared following the initial therapy.

Adjuvant therapy: Additional cancer treatment given after the primary treatment to lower the risk that the cancer will come back. Adjuvant therapy may include chemotherapy, radiation therapy, hormone therapy, targeted therapy, or biological therapy.

Neoadjuvant therapy: Treatment given as a first step to shrink a tumor before the main treatment, which is usually surgery, is given. Examples of neoadjuvant therapy include chemotherapy, radiation therapy, and hormone therapy. It is a type of induction therapy.

Palliative therapy: Treatment given to help relieve the symptoms and reduce the suffering caused by cancer or other life-threatening diseases. Palliative therapy may help a person feel more comfortable, but it does not treat or cure the disease. For example, surgery, radiation therapy, or chemotherapy may be given to remove, shrink, or slow the growth of a tumor that is causing pain. Palliative therapy may be given with other treatments from the time of diagnosis until the end of life.

So can you help to to do the "One-class classifiers" classification task based on these information? When I tell you "Please help me to catogorize the content: XXXX" then it means I need you to do the classification tasks. and the tasks is a "One-class" task, you should tell me the answer in the format of :
| Lines of Therapy | Reason |
| ---- | ---- |
| XXXX | XXXX |

Do you understand?"""},
               {"role": "assistant", "content": "Yes, I understand. I will help you to categorize the content based on the definitions provided. When you provide the content, I will classify it as one of the Lines of Therapy and give a reason for the classification in the specified format."},
               {"role": "user", "content": f"Please help me to catogorize the content: \n"
                                           f"Input:{abstract}\n"
                                           f"Output:"},
               ]
    return ou.chat_completion(message, temperature=0.0)


[print(gpt_extraction(x)) for x in meeting_abstract]

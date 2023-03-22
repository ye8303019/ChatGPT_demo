import utils.chunk_utils as cu
import utils.openai_utils as ou

token_threshold = 1800
model = "gpt-3.5-turbo"
meeting_abstract = cu.get_file_content("abstract_24", token_threshold, model)


# if only CTGov clinical trials could be listed in the abstract
def get_evaluation(abstract):
    message = [{"role": "system", "content": "Now you are clinical trial researcher"},
               {"role": "user", "content": f"you know well about the clinical result and also the clinical "
                                           f"conclusion, you know whether it's 'superiority' or 'positive' or "
                                           f"'non-superiority' or 'non-inferiority' or 'similar' or 'negative', "
                                           f"Usually, in a paper of clinical study, there would be multiple parts, "
                                           f"in 'Purpose' or 'Background' or 'Objective' and so on, the content will "
                                           f"reveal the original purpose for this study, whether it's 'superiority' "
                                           f"or 'positive' or 'non-superiority' or 'non-inferiority' or 'similar' or "
                                           f"'negative' and at the same time. In the 'Results' or 'Conclusions' part, "
                                           f"the content will tell us whether it's 'superiority' or 'positive' or "
                                           f"'non-superiority' or 'non-inferiority' or 'similar' or 'negative' for "
                                           f"the true result of the study and if 'Paragraph' is 'Purpose' or "
                                           f"'Background' or 'Objective' and so on, then the 'Purpose Type' is "
                                           f"'Original Purpose', if 'Paragraph' is 'Results' , then the 'CT Purpose' "
                                           f"is 'Result Evaluation' if 'Paragraph' is 'Conclusions', then the 'CT "
                                           f"Purpose' is 'Author Evaluation', and now here is a content from a paper, "
                                           f"can you tell me it's 'superiority' or 'positive' or 'non-superiority' or "
                                           f"'non-inferiority' or 'similar' or 'negative' ? Please reply in the table "
                                           f"like below: \n "
                                           f"| Paragraph| Purpose Type |Type | Reason | \n "
                                           f"| -------- | --------------- | --------------- | ---- | \n "
                                           f"| XXXX | XXXX | XXXX | XXXX | \n "
                                           f"For example, \n"
                                           f"| Paragraph | Purpose Type | Type | Reason | \n "
                                           f"| -------- | --------------- | --------------- | ---- | \n "
                                           f"| Purpose | Original Purpose | non-inferiority | XXXX | \n "
                                           f"| Conclusions | Author Evaluation | | similar | XXXX | \n "
                                           f"So the content is: \n"
                                           f"{abstract} "}]
    return ou.chat_completion(message, temperature=0.4)


[print(get_evaluation(x)) for x in meeting_abstract]

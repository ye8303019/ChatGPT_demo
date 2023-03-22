import utils.chunk_utils as cu
import utils.openai_utils as ou

token_threshold = 1800
model = "gpt-3.5-turbo"
meeting_abstract = cu.get_file_content("abstract_10", token_threshold, model)


# if only CTGov clinical trials could be listed in the abstract
def get_evaluation(abstract):
    message = [{"role": "system", "content": "Now you are a clinical trail  organizer"},
               {"role": "user", "content": f"you can read and detect how many patient are needed for a trial from a "
                                           f"paper. So please extract or calculate the total patients which are "
                                           f"needed for the trail from the paper content, and reply in the format of \n"
                                           f": | Total Patients Number | Reason | \n "
                                           f"| --------------- | ------- | \n "
                                           f"| XXX | XXX | \n "
                                           f"Please notice that the 'Patients Number' should only be "
                                           f"a number, and also in the paper, the author usually user N=X to present "
                                           f"the patients number, for example: Part B enrollment is ongoing (N=9 in "
                                           f"ccRCC cohort) means 9 patients for PartB. If you don't know then "
                                           f"returns 'None' and also some times you need to calculate the number but "
                                           f"not just extract it from the paper, for example in the following "
                                           f"paragraph: \n"
                                           f"'As of Dec 2, 2022, the study enrolled 19 pts in Part A1 and "
                                           f"15 in Part A2 with no DLTs observed. The median prior lines of therapies "
                                           f"were 4 ("
                                           f"range 1-10). In Part A1, the most common treatment-related AEs (TRAEs, "
                                           f">10%) of any grade were fatigue (16%, n=3), decreased appetite and "
                                           f"nausea (each 11%, n=2). Best response of stable disease (SD) was "
                                           f"observed in 8 pts. All 3 ovarian cancer pts were stable for 25 to 42 "
                                           f"weeks. In Part A2, the TRAEs (>10%) of any grade were rash "
                                           f"maculo-papular (33%, n=5), pruritus (27%, n=4), rash (20%, n=3), "
                                           f"diarrhea and pemphigoid (each 13%, n=2). One confirmed RECIST 1.1 "
                                           f"partial response (cPR) was observed at 800mg in a pt with anti-PD-1 "
                                           f"resistant ccRCC who stayed on study for 30 weeks. Of 9 pts with best "
                                           f"response of SD, 5 were stable >16 weeks. SRK-181 treatment resulted in "
                                           f"increased levels of circulatory TGFβ1, indicating target engagement. "
                                           f"Part B enrollment is ongoing (N=9 in ccRCC cohort); two cPR were "
                                           f"observed in pts with anti-PD-1 resistant ccRCC.' \n"
                                           f"In this pargraph, there are 'Part A1', 'Part A2', and 'PartB', and from "
                                           f"'the study enrolled 19 pts in Part A1 and 15 in Part A2 with no DLTs "
                                           f"observed.' we know there are 19 patients in PartA1, 15 patients in "
                                           f"PartA2, so now the patient number may at least 19+15 = 34 , "
                                           f"then from another part of the paragraph : 'Part B enrollment is ongoing "
                                           f"(N=9 in ccRCC cohort)', we know there are 9 patients for partB, "
                                           f"so the final totoal patients number should be 34+9 = 43, then the answer "
                                           f"is: \n "
                                           f"| Patients Number | Reason | \n "
                                           f"| --------------- | ------- | \n "
                                           f"| 19 | the study enrolled 19 pts in Part A1 and 15 in Part A2 with no "
                                           f"DLTs observed. | \n "
                                           f"| 15 | the study enrolled 19 pts in Part A1 and 15 "
                                           f"in Part A2 with no DLTs observed. | \n "
                                           f"| 9 | Part B enrollment is "
                                           f"ongoing (N=9 in ccRCC cohort) | \n "
                                           f"| 43 | In this paragraph, "
                                           f"there are 'Part A1', 'Part A2', and 'PartB', and from ' the study "
                                           f"enrolled 19 pts in Part A1 and 15 in Part A2 with no DLTs observed.' we "
                                           f"know there are 19 patients in PartA1, 15 patients in PartA2, "
                                           f"so now we know the patient number may at least 19+15 = 34 , "
                                           f"then from 'Part B enrollment is ongoing (N=9 in ccRCC cohort)', "
                                           f"we know there are 9 patients for partB, so the final total patients "
                                           f"number should be 34+9 = 43 | \n "
                                           f""
                                           f"Now the content of the paper is as below, please tell me the answer: \n "
                                           f"{abstract} "}]
    return ou.chat_completion(message, temperature=0.2)


[print(get_evaluation(x)) for x in meeting_abstract]

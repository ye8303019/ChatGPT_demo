import main
import utils.chunk_utils as cu
import utils.openai_utils as ou
import utils.json_utils as ju

token_threshold = 1800
model = main.OPENAI_CHAT_MODEL


def format_answer(answers):
    dicts = []
    for answer in answers:
        if answer:
            my_dict_list = ju.json2dicts(answer)
            for my_dict in my_dict_list:
                count = 0
                for my_value in my_dict.values():
                    if my_value == 'None':
                        count += 1
                if count != len(my_dict.values()):
                    dicts.append(my_dict)
    return dicts


# if only CTGov clinical trials could be listed in the abstract
def get_evaluation(abstract):
    abstract = abstract.replace("\"", " ").replace("'", " ")
    # message = [{"role": "system", "content": "Now you are a clinical trail  organizer"},
    #            {"role": "user", "content": f"you can read and detect how many patient are needed for a trial from a "
    #                                        f"paper. So please extract or calculate the total patients which are "
    #                                        f"needed for the trail from the paper content, and reply in the format of "
    #                                        f"json like\n "
    #                                        f"[{{"
    #                                        f"'Total Patients Number': String,\n"
    #                                        f"'Reason': String\n"
    #                                        f"}}]"
    #                                        f"Please notice that the 'Patients Number' should only be "
    #                                        f"a number, and also in the paper, the author usually user N=X to present "
    #                                        f"the patients number, for example: Part B enrollment is ongoing (N=9 in "
    #                                        f"ccRCC cohort) means 9 patients for PartB. If you don't know then "
    #                                        f"returns 'None' and also some times you need to calculate the number but "
    #                                        f"not just extract it from the paper, and please put the calcuation steps "
    #                                        f"in the 'Reason', for example in the following "
    #                                        f"paragraph: \n"
    #                                        f"'As of Dec 2, 2022, the study enrolled 19 pts in Part A1 and "
    #                                        f"15 in Part A2 with no DLTs observed. The median prior lines of therapies "
    #                                        f"were 4 ("
    #                                        f"range 1-10). In Part A1, the most common treatment-related AEs (TRAEs, "
    #                                        f">10%) of any grade were fatigue (16%, n=3), decreased appetite and "
    #                                        f"nausea (each 11%, n=2). Best response of stable disease (SD) was "
    #                                        f"observed in 8 pts. All 3 ovarian cancer pts were stable for 25 to 42 "
    #                                        f"weeks. In Part A2, the TRAEs (>10%) of any grade were rash "
    #                                        f"maculo-papular (33%, n=5), pruritus (27%, n=4), rash (20%, n=3), "
    #                                        f"diarrhea and pemphigoid (each 13%, n=2). One confirmed RECIST 1.1 "
    #                                        f"partial response (cPR) was observed at 800mg in a pt with anti-PD-1 "
    #                                        f"resistant ccRCC who stayed on study for 30 weeks. Of 9 pts with best "
    #                                        f"response of SD, 5 were stable >16 weeks. SRK-181 treatment resulted in "
    #                                        f"increased levels of circulatory TGFβ1, indicating target engagement. "
    #                                        f"Part B enrollment is ongoing (N=9 in ccRCC cohort); two cPR were "
    #                                        f"observed in pts with anti-PD-1 resistant ccRCC.' \n"
    #                                        f"In this paragraph, there are 'Part A1', 'Part A2', and 'PartB', and from "
    #                                        f"'the study enrolled 19 pts in Part A1 and 15 in Part A2 with no DLTs "
    #                                        f"observed.' we know there are 19 patients in PartA1, 15 patients in "
    #                                        f"PartA2, so now the patient number may at least 19+15 = 34 , "
    #                                        f"then from another part of the paragraph : 'Part B enrollment is ongoing "
    #                                        f"(N=9 in ccRCC cohort)', we know there are 9 patients for partB, "
    #                                        f"so the final total patients number should be 34+9 = 43, then the answer "
    #                                        f"is: \n "
    #                                        f"[{{"
    #                                        f"'Total Patients Number': '43',\n"
    #                                        f"'Reason': 'In this paragraph, "
    #                                        f"there are 'Part A1', 'Part A2', and 'PartB', and from ' the study "
    #                                        f"enrolled 19 pts in Part A1 and 15 in Part A2 with no DLTs observed.' we "
    #                                        f"know there are 19 patients in PartA1, 15 patients in PartA2, "
    #                                        f"so now we know the patient number may at least 19+15 = 34 , "
    #                                        f"then from 'Part B enrollment is ongoing (N=9 in ccRCC cohort)', "
    #                                        f"we know there are 9 patients for partB, so the final total patients "
    #                                        f"number should be 34+9 = 43'\n"
    #                                        f"}}]"
    #                                        f"Now the content of the paper is as below, please tell me the total "
    #                                        f"patient number and the reason: \n "
    #                                        f"{abstract} "}]
    message = [{"role": "system", "content": "Now you are a clinical trail  organizer"},
               {"role": "user", "content": f"you can read and detect how many patient are needed for a trial from a "
                                           f"paper. So please tell me how many patients have been confirmed to be "
                                           f"enrolled into the group, and also tell me the detail reason and your "
                                           f"analysis steps and put them into the field 'Reason', reply in the "
                                           f"format like:\n "
                                           f"Json:"
                                           f"[{{"
                                           f"'Overall Enrollment': 'Number'}}]\n"
                                           f"Reason:\n"
                                           f"The reason which you get the overall enrollment\n\n"
                                           f"Rules:\n"
                                           f"1. If you don't know, please just reply 'None' and put it in the "
                                           f"'Overall Enrollment' field. \n"
                                           f"2. The 'Overall Enrollment' field should only "
                                           f"be a number \n\n "
                                           f"Knowledge:\n"
                                           f"1. We usually use (N=X) to present the number of enrollment, "
                                           f"for example: (N=7) means 7 patients for the specific trial.\n"
                                           f"2. We usually use 'pts' as the abbreviation for 'patients'\n\n"
                                           f"So tell me how many patients been enrolled for overall for the content "
                                           f"below \n"
                                           f"The paper content: \n "
                                           f"{abstract} "}]
    response = ou.chat_completion(message, temperature=0.9, timeout=20)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [(ju.json_extraction(get_evaluation(x))) for x in abstracts]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))


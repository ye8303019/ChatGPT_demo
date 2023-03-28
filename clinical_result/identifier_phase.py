import utils.chunk_utils as cu
import utils.openai_utils as ou
import utils.json_utils as ju
import main

token_threshold = 1800
model = main.OPENAI_MODEL


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
def gpt_extraction(abstract):
    abstract = abstract.replace("\"", " ").replace("'", " ")
    message = [{"role": "system", "content": "Now you play a role of a excellent clinical trial researcher, you know "
                                             "well about the clinical trials"},
               {"role": "user", "content": f"The list of argument roles corresponding to the event type "
                                           f"[Clinical Trials : Study Phase] is ['Identifier', 'Phase'], "
                                           f"and I will give you a sentence "
                                           f"or paragraph or article, please extract the event arguments according "
                                           f"to the argument roles, and return them in the form of a json schema like "
                                           f"below. "
                                           f"If no argument role has a corresponding argument content, "
                                           f"the argument content returns 'None'.  "
                                           f"[{{"
                                           f"'Identifier': String,\n"
                                           f"'Phase': String,\n"
                                           f"'Drug': String\n"
                                           f"}}]"
                                           f"Remember some important concepts:\n"
                                           f"1 - there is only one main identifier which is related to the study "
                                           f"result \n "
                                           f"2 - The definition of the phase is : A clinical trial phase is a stage "
                                           f"in the process of testing a new treatment or intervention in human "
                                           f"subjects. The process of clinical trials typically involves several "
                                           f"distinct phases, each with its own objectives, methods, and outcomes. "
                                           f"The phases are designed to gradually increase the amount of information "
                                           f"and evidence available about the safety, efficacy, and optimal use of "
                                           f"the treatment being tested. The enumeration of the 'Phase' could mapping "
                                           f"to [ "
                                           f"'Early Phase 1', 'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 2/3', "
                                           f"'Phase 3', 'Phase4']\n"
                                           f"e.g.1: \n "
                                           f"To report the results of a pre-planned interim analysis of Low-PV, "
                                           f"a Phase I/II "
                                           f"investigator driven randomized trial (NCT030030025) conducted to assess "
                                           f"the "
                                           f"benefit/risk profile of Ropeginterferon alfa-2b versus phlebotomy alone ("
                                           f"standard therapy) in low-risk patients with PV. \n"
                                           f"because Low-PV is refer to Low Pharmacovigilance but not a code\n"
                                           f"Then, the json should looks like: \n "
                                           f"[{{"
                                           f"'Identifier': 'NCT030030025',\n"
                                           f"'Phase': 'Phase 1/2',\n"
                                           f"'Drug': String\n"
                                           f"}}]"
                                           f"e.g.2:\n"
                                           f"Adjuvant pembrolizumab (pembro) for advanced renal cell carcinoma (RCC) "
                                           f"across "
                                           f"UCLA Integrated Staging System (UISS) risk groups and disease stage: "
                                           f"Subgroup analyses from the KEYNOTE-564 study.Background: Adjuvant pembro "
                                           f"prolonged disease-free survival (DFS) for patients (pts) with RCC at "
                                           f"increased risk of recurrence after nephrectomy in the Ph1b "
                                           f"KEYNOTE-564 study (NCT03142334). This post hoc exploratory analysis "
                                           f"evaluated efficacy of adjuvant pembro in pt subgroups based on UISS and "
                                           f"disease stage.Assuming the  0/1 lines of prior therapy ORR of 40%, "
                                           f"40 pts would give a 95% CI with a lower limit of 25% (CI is 0.25 to "
                                           f"0.57) for ORR\n "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': 'NCT03142334',\n"
                                           f"'Phase': 'Phase 1b,'\n"
                                           f"'Drug': 'Pembrolizumab '\n"
                                           f"}}]"
                                           f"e.g.3:\n"
                                           f"Prognostic stratification by the Meet-URO score in a real-world elderly "
                                           f"population of patients (pts) with advanced or metastatic  renal cell "
                                           f"carcinoma (mRCC) "
                                           f"receiving cabozantinib: A subanalysis of the prospective ZEBRA study ("
                                           f"Meet-URO 9). Further applications of the Meet-URO score in mRCC pts "
                                           f" that previously received ≥2 lines of therapy including a platinum "
                                           f"doublet were treated with 4 mg RRx-001 IV once per week. . Clinical "
                                           f"trial information: 2018/116/PU.Eligible pts (age ≥18 y) had "
                                           f"histologically confirmed, CD20-positive R/R NHL "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': '2018/116/PU',\n"
                                           f"'Phase': 'None',\n"
                                           f"'Drug': 'Cabozantinib '\n"
                                           f"}}]"
                                           f"e.g.4:\n"
                                           f"Long-term results of a phase 2 trial of crenolanib combined with 7+3 "
                                           f"chemotherapy in adults with newly diagnosed FLT3 mutant AML. "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': 'None',\n"
                                           f"'Phase': 'Phase 2',\n"
                                           f"'Drug': 'Crenolanib'\n"
                                           f"}}]"
                                           f"e.g.5:\n"
                                           f"Results from a phase 1a/1b study of botensilimab (BOT), a novel "
                                           f"innate/adaptive immune activator, plus balstilimab (BAL; anti-PD-1 "
                                           f"antibody) in metastatic heavily pretreated microsatellite stable "
                                           f"colorectal cancer (MSS CRC).Background: BOT promotes optimized T cell "
                                           f"priming, activation and memory formation by strengthening antigen "
                                           f"presenting cell/T cell co-engagement. As an Fc-enhanced next-generation "
                                           f"anti–CTLA-4 antibody, BOT also promotes intratumoral regulatory T cell "
                                           f"depletion and reduces complement fixation. We present results from "
                                           f"patients with MSS CRC treated with BOT + BAL in an expanded phase 1a/1b "
                                           f"study "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': 'None',\n"
                                           f"'Phase': 'Phase 1a/1b',\n"
                                           f"'Drug': 'botensilimab'\n"
                                           f"}}]\n\n"
                                           f"Now, use this rule to extract the event from the content below : \n "
                                           f"{abstract}"
                }]
    response = ou.chat_completion(message, temperature=0.6)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [(ju.json_extraction(gpt_extraction(x))) for x in abstracts]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))




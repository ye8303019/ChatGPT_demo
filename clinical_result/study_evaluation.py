import utils.chunk_utils as cu
import utils.openai_utils as ou
import utils.json_utils as ju
import main

token_threshold = 3500
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
    if len(dicts) == 0:
        dicts.append({"Evaluation": "None"})
    return dicts


# if only CTGov clinical trials could be listed in the abstract
def get_evaluation(abstract):
    abstract = abstract.replace("\"", " ").replace("'", " ")

    message = [{"role": "user",
                "content": f"In the papar for the clinical trial study, it's usually organized in multiple parts, "
                           f"like 'Background','Results','Conclusions','Interpretations','Methods', 'Objective' and "
                           f"so on, please extract the Title and Conclusion(interpretation) in the give content, "
                           f"remember don't overwrite or change the given content, just return the original text "
                           f"which you think they are Title or Conclusions(Interpretations):\n "
                           f"'''\n"
                           f"{abstract}\n"
                           f"'''\n"
                           f"Reply in the format of:\n"
                           f"Title: xxxx\n"
                           f"Conclusions(Interpretations): xxxx"}]
    response = ou.chat_completion(message, temperature=0.9, timeout=25)
    print(response)

    message = [{"role": "system", "content": "Now you are clinical trial researcher"},
               {"role": "user", "content": f"Input:\n"
                                           f"In the 22 patients with r/r AML, median OS was 3.0 months in the nintedanib and 3.6 months in the placebo arm (P = 0.36).   One patient in the nintedanib and two patients in the placebo arm achieved a CR and entered maintenance treatment.   Nintedanib showed no superior therapeutic activity over placebo when added to LDAC in elderly AML patients considered unfit for intensive chemotherapy.\n"
                                           f"Q:What's the evalution for the input? Only need to return one type of evalution, multiple items are forbidden. If you don't know, return 'None' in the field 'Evaluation' in json\n"
                                           f"A:\n"
                                           f"Json:\n"
                                           f"[{{'Evaluation':'Non-Superiority'}}]\n"
                                           f"Reason:\n"
                                           f"Becase the content mentioned 'no superior therapeutic activity over placebo ', which means after the study, the author found it's no any improvement. so the answer is 'Non-Superiority'\n"
                                           f"\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Background: In the global, Phase 3 HIMALAYA study (NCT03298451) in uHCC, a single priming dose of T plus regular interval D (STRIDE) significantly improved overall survival (OS) vs sorafenib (S), and D was noninferior to S (Abou-Alfa et al. NEJM Evid 2022; https://doi.org/10.1056/EVIDoa2100070). HCC aetiology varies globally and may influence response to immunotherapy. HBV is predominant in most Asian countries, whereas HCV or nonviral aetiologies are more common in Japan and Western countries. Thus, we analysed outcomes in patients (pts) enrolled in Asia, excluding Japan. Conclusions:\n"
                                           f"STRIDE improved outcomes vs S for pts in Asia, consistent with the global population. These results support the benefits of STRIDE for pts with uHCC in the Asia-Pacific region, including Hong Kong and Taiwan.\n"
                                           f"Q:What's the evalution for the input? Only need to return one type of evalution, multiple items are forbidden. If you don't know, return 'None' in the field 'Evaluation' in json\n"
                                           f"A:\n"
                                           f"Json:\n"
                                           f"[{{'Evaluation':'Superiority'}}]\n"
                                           f"Reason:\n"
                                           f"Becase the content mentioned for background, the author found STRIDE significantly improved overall survival (OS) vs sorafenib (S), and after study, in the conclusions, author mentioned that STRIDE improved outcomes vs S for pts in Asia, consistent with the global population, which means the evaluation is 'Superiority'\n"
                                           f"\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"In this planned final analysis, with extended follow up of 5 years in the randomized cohort and 2 years in the Ext cohort, the improved efficacy of Pola+BR persisted.  Median DoR was longer with increased follow-up, indicating Pola+BR leads to a durable benefit in responding pts.  Median PFS and OS were longer with Pola+BR compared with BR, consistent with previous results.  No new safety signals were identified.  These findings provide further evidence of the effectiveness of Pola+BR for the treatment of R/R DLBCL.\n"
                                           f"Q:What's the evalution for the input? Only need to return one type of evalution, multiple items are forbidden. If you don't know, return 'None' in the field 'Evaluation' in json\n"
                                           f"A:\n"
                                           f"Json:\n"
                                           f"[{{'Evaluation':'positive'}}]\n"
                                           f"Reason:\n"
                                           f"Becase the study demonstrate 'durable benefit in responding pts' and also the final study result is 'consistent with previous results', and 'These findings provide further evidence of the effectiveness of Pola+BR for the treatment of R/R DLBCL', so which means the evaluation of the study is 'positive'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Conclusions: DHP107 as a second-line treatment of AGC was non-inferior to paclitaxel for PFS;  other efficacy and safety parameters were comparable.  DHP107 is the first oral paclitaxel with proven efficacy/safety for the treatment of AGC.\n"
                                           f"Q:What's the evalution for the input? Only need to return one type of evalution, multiple items are forbidden. If you don't know, return 'None' in the field 'Evaluation' in json\n"
                                           f"A:\n"
                                           f"Json:\n"
                                           f"[{{'Evaluation':'non-inferiority'}}]\n"
                                           f"Reason:\n"
                                           f"Becase the study demonstrate 'DHP107 as a second-line treatment of AGC was non-inferior to paclitaxel for PFS' which means the evaluation of the study is 'positive'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Conclusions:\n"
                                           f"Combination of abemaciclib plus pembrolizumab demonstrated a generally tolerable safety profile with numerically higher rate of transaminase elevations than reported for the individual treatments.  Compared to historical data for abemaciclib monotherapy in a similar pt population, a numerically higher but not obviously different ORR, PFS, and OS was observed.\n"
                                           f"Q:What's the evalution for the input? Only need to return one type of evalution, multiple items are forbidden. If you don't know, return 'None' in the field 'Evaluation' in json\n"
                                           f"A:\n"
                                           f"Json:\n"
                                           f"[{{'Evaluation':'Similar'}}]\n"
                                           f"Reason:\n"
                                           f"Becase the content mentioned 'Compared to historical data for abemaciclib monotherapy in a similar pt population' which means the evaluation of the study is 'Similar'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Interpretation: There was no evidence that S44819 improved clinical outcome in patients after ischaemic stroke, and thus S44819 cannot be recommended for stroke therapy.  The concept of tonic inhibition after stroke should be re-evaluated in humans.\n"
                                           f"Q:What's the evalution for the input? Only need to return one type of evalution, multiple items are forbidden. If you don't know, return 'None' in the field 'Evaluation' in json\n"
                                           f"A:\n"
                                           f"Json:\n"
                                           f"[{{'Evaluation':'Negative'}}]\n"
                                           f"Reason:\n"
                                           f"Becase the content mentioned 'no evidence that S44819 improved clinical outcome in patients', the no evidence is the key, and the author also mentioned that the method 'should be re-evaluated' which means the evaluation of the study is 'Negative'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"{response}\n"
                                           f"\n"
                                           f"(REMEMBER! ONLY ONE EVALUATION TYPE IS ALLOWED, RETUREN THE ONE YOU THINK MOST LIKELY!!! AND ONLY RETURN IN THE ENUMERATION OF：Superiority,Positive,Non-superiority,Non-inferiority,Similar,Negative and None)\n"
                                           f"\n"
                                           f"A: "}]
    response = ou.chat_completion(message, temperature=0.4)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [ju.json_extraction(get_evaluation(abstracts[0]))]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))


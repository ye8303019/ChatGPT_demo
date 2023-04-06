import utils.chunk_utils as cu
import utils.openai_utils as ou
import utils.json_utils as ju
import main

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
def gpt_extraction(abstract):
    abstract = abstract.replace("\"", " ").replace("'", " ")
    message = [{"role": "system", "content": "Now you play a role of a excellent clinical trial researcher, you know "
                                             "well about the clinical trials"},
               {"role": "user", "content": f"The list of argument roles corresponding to the event type "
                                           f"[Clinical Trials : Target Indication] is ['Target "
                                           f"Indication'], "
                                           f"and I will give you a sentence "
                                           f"or paragraph or article, please extract the event arguments according "
                                           f"to the argument roles, and return them in the form of a json schema like "
                                           f"below. "
                                           f"If no argument role has a corresponding argument content, "
                                           f"the argument content returns 'None'.  "
                                           f"[{{"
                                           f"'Target Indication': String\n"
                                           f"}}]\n"
                                           f"e.g.1: \n "
                                           f"TCOLUMBUS 5-Year Update: A Randomized, Open-Label, Phase III Trial of "
                                           f"Encorafenib Plus Binimetinib Versus Vemurafenib or Encorafenib in "
                                           f"Patients With BRAF V600-Mutant Melanoma. Abstract Purpose: Combination "
                                           f"treatment with BRAF and MEK inhibitors has demonstrated benefits on "
                                           f"progression-free survival (PFS) and overall survival (OS) and is a "
                                           f"standard of care for the treatment of advanced BRAF V600-mutant "
                                           f"melanoma. Here, we report the 5-year update from the COLUMBUS trial ("
                                           f"ClinicalTrials.gov identifier: NCT01909453).\n "
                                           f"Then, the json should looks like: \n "
                                           f"[{{"
                                           f"'Target Indication': 'Melanoma'\n"
                                           f"}}]\n"
                                           f"e.g.2:\n"
                                           f"Real-world clinical effectiveness and safety of olaparib monotherapy in "
                                           f"HER2-negative gBRCA-mutated metastatic breast cancer: Phase IIIb LUCY "
                                           f"interim analysis.Research Funding Pharmaceutical/Biotech CompanyThis "
                                           f"study was sponsored by AstraZeneca and is part of an alliance between "
                                           f"AstraZeneca and Merck Sharp & Dohme Corp., a subsidiary of Merck & Co., "
                                           f"Inc., Kenilworth, NJ, USA (MSD).Background:OlympiAD (NCT02000622) "
                                           f"demonstrated the benefit of olaparib over standard of care in patients ("
                                           f"pts) with HER2-negative (HER2-) metastatic breast cancer (MBC) and "
                                           f"germline BRCA mutations (gBRCAm). LUCY (NCT03286842) aimed to provide "
                                           f"additional data on the real-world effectiveness and safety of olaparib "
                                           f"monotherapy in this setting.Results:From Oct 2018-Sept 2019, 252 pts "
                                           f"were enrolled (160 sites, 15 countries; mean age 46.2 [range 22-75] "
                                           f"years; 73.4% ECOG PS 0). Median total treatment duration: 7.9 months ("
                                           f"mo; range 0.2-20.0). Median PFS: 8.1 mo (95% confidence interval [CI] "
                                           f"6.9, 8.7; 166 events [65.9%]). Clinical trial information: NCT03286842. "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Target Indication': 'metastatic breast cancer\n "
                                           f"}}]\n"
                                           f"e.g.3:\n"
                                           f"R3245 Daratumumab Plus Lenalidomide and Dexamethasone (D-Rd) Versus "
                                           f"Lenalidomide and Dexamethasone (Rd) in Transplant-Ineligible Patients ("
                                           f"Pts) with Newly Diagnosed Multiple Myeloma (NDMM): Clinical Assessment "
                                           f"of Key Subgroups of the Phase 3 Maia Study "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Target Indication': 'Newly Diagnosed Multiple Myeloma'\n "
                                           f"}}]\n"
                                           f"e.g.4:\n"
                                           f"67O - Outcomes in the Asian subgroup of the phase III HIMALAYA study of "
                                           f"tremelimumab (T) plus durvalumab (D) in unresectable hepatocellular "
                                           f"carcinoma (uHCC) "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Target Indication': 'unresectable hepatocellular carcinoma'\n "
                                           f"}}]"
                                           f"e.g.6:\n"
                                           f"A phase Ib/II study of the combination of lenvatinib (L) and eribulin ("
                                           f"E) in advanced liposarcoma (LPS) and leiomyosarcoma (LMS) (LEADER): "
                                           f"Efficacy updates.There are limited treatment options for advanced LPS "
                                           f"and LMS, the two most common histologies in soft tissue sarcoma. "
                                           f"Patients (pts) treated with E had an improved overall survival (OS) "
                                           f"compared to dacarbazine but with an unsatisfactory 4% objective response "
                                           f"rate (ORR). Early studies of L, a multi-targeted anti-angiogenic "
                                           f"inhibitor, had suggested efficacy in sarcoma pts. We hypothesized that "
                                           f"the L+E could potentiate the treatment efficacy in advanced LMS and LPS. "
                                           f"Then, the json looks like:\n"
                                           f"[{{\n"
                                           f"'Target Indication': 'advanced liposarcoma, leiomyosarcoma'\n "
                                           f"}}]\n\n"
                                           f"Now, use this rule to extract the event from the content below : \n "
                                           f"{abstract}"
                }]
    response = ou.chat_completion(message, temperature=0.0)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [(ju.json_extraction(gpt_extraction(x))) for x in abstracts]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))




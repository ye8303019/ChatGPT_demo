import main
import utils.chunk_utils as cu
import utils.openai_utils as ou
import utils.json_utils as ju

token_threshold = 2500
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
    abstract = abstract.replace("'", " ").replace("'", " ")
    message = [{"role": "system", "content": "Now you are a clinical trail researcher"},
               dict(role="user", content=f"Knowledge: \n"
                                         f"1. The 'Biomarker' in an article or a paper usually been mentioned in the "
                                         f"title or the results part or the conclusion part. It's the main subject "
                                         f"of a clinical trial related literature, This biomarker will be discussed "
                                         f"throughout the article, as well as the corresponding experimental "
                                         f"results\n "
                                         f"2. The 'Biomarker' is a biological molecule found in blood, "
                                         f"other body fluids, or tissues that is a sign of a normal or abnormal "
                                         f"process, or of a condition or disease. \n "
                                         f"3. The 'Biomarker' must combine with some qualifiers, like: "
                                         f"overexpressing, "
                                         f"alterations, "
                                         f"amplified, positive, mutated, amplification,deletion,negative,"
                                         f"non-amplified,fusions,Rearranged, wild-type and so on. Some times even "
                                         f"use '-', "
                                         f"'-low' and so on. \n"
                                         f"For example:\n "
                                         f"Question: Does 'overexpression of ACOX1' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'ACOX1' is a biomarker?\n"
                                         f"Answer: No\n"
                                         f"Question: Does 'high DLL3 expression' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'DLL3' is a biomarker?\n"
                                         f"Answer: No\n"
                                         f"Question: Does '(PD-L1)-expressing' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'RET fusion-positive' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'RET' is a biomarker?\n"
                                         f"Answer: No\n"
                                         f"Question: Does 'HER2-Positive' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'HER2' is a biomarker?\n"
                                         f"Answer: No\n"
                                         f"Question: Does 'INI1-negative' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'INI1' is a biomarker?\n"
                                         f"Answer: No\n"
                                         f"Question: Does 'MET amplification/exon 14 deletion' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'MET' is a biomarker?\n"
                                         f"Answer: No\n"
                                         f"Question: Does 'EGFR-mutated' is a biomarker?\n"
                                         f"Answer: Yes\n"
                                         f"Question: Does 'EGFR' is a biomarker?\n"
                                         f"Answer: No\n"
                                         # f"4. The 'Biomarker' must not be an indication. For example\n"
                                         # f"Question: Does 'de novo metastatic castration sensitive prostate cancer ("
                                         # f"mCSPC)' is a biomarker?\n "
                                         # f"Answer: No, it's an indication\n"
                                         # f"Question: Does 'relapsed/refractory multiple myeloma' is a biomarker?\n"
                                         # f"Answer: No, it's an indication\n"
                                         f"\n\n"
                                         f"Reply Format Rules:\n"
                                         f"1. reply format should be a json like below:\n "
                                         f"[{{"
                                         f"'Biomarker': String,\n"
                                         f"'Target Indication': String\n"
                                         f"}}]\n\n"
                                         f"2. If you don't know, please just reply 'None' and put it in the "
                                         f"'Biomarker' field. \n "
                                         f"For example: \n"
                                         f"[{{"
                                         f"'Biomarker': 'None',\n"
                                         f"'Target Indication': 'None'\n"
                                         f"}}]\n\n"
                                         f"3. If you found multiple biomarker, the reply should be like:\n "
                                         f"[{{"
                                         f"'Biomarker': 'HR−',\n"
                                         f"'Target Indication': 'XXXX'\n"
                                         f"}},{{"
                                         f"'Biomarker': 'HER2-low',\n"
                                         f"'Target Indication': 'XXXX'\n"
                                         f"}}]\n\n"
                                         f"Based on the 'Knowledge' and 'Reply Format Rules' above, here are some "
                                         f"examples: \n "
                                         # f"e.g.1\n"
                                         # f"Input:\n"
                                         # f"Trastuzumab deruxtecan (T-DXd) + durvalumab (D) as first-line (1L) "
                                         # f"treatment for unresectable locally advanced/metastatic hormone "
                                         # f"receptor-negative (HR−), HER2- low breast cancer: updated results from "
                                         # f"BEGONIA, a phase 1b/2 study. Background: Patients with HR− "
                                         # f"advanced/metastatic breast cancer (a/mBC) with a low level of HER2 ("
                                         # f"immunohistochemistry [IHC] score 1+ or IHC 2+ and negative in situ "
                                         # f"hybridization [ISH]) have poor prognosis. Combining 1L chemotherapy with "
                                         # f"immune checkpoint inhibitors can modestly improve outcomes vs "
                                         # f"chemotherapy alone, but treatment benefit is largely seen in patients "
                                         # f"with PD-L1+ disease. BEGONIA (NCT03742102) is an ongoing 2-part, "
                                         # f"open-label platform study, evaluating safety and efficacy of D, "
                                         # f"an anti–PD-L1 antibody, combined with other novel therapies in 1L "
                                         # f"triple-negative a/mBC, including HR−, HER2-low disease. T-DXd is a "
                                         # f"trastuzumab-topoisomerase I inhibitor antibody-drug conjugate that "
                                         # f"improves survival in patients with previously treated HR−, HER2-low mBC "
                                         # f"(NCT03734029; Modi NEJM 2022). \n"
                                         # f"Answer:"
                                         # f"[{{"
                                         # f"'Biomarker': 'HR−'\n"
                                         # f"}},{{"
                                         # f"'Biomarker': 'HER2-low'\n"
                                         # f"}}]\n"
                                         f"e.g.1\n"
                                         f"Input:\n"
                                         f"Abstract P4-21-07: Preliminary safety and efficacy of first-line "
                                         f"pertuzumab combined with trastuzumab and taxane therapy in patients ≥65 "
                                         f"years with HER2-positive locally recurrent/metastatic breast cancer: "
                                         f"Subgroup analyses of the PERUSE study \n "
                                         f"Answer:"
                                         f"[{{"
                                         f"'Biomarker': 'HER2-positive',\n"
                                         f"'Target Indication':'locally recurrent/metastatic breast cancer'\n"
                                         f"}}]\n"
                                         f"e.g.2\n"
                                         f"Input:\n"
                                         f"Because c-MET and VEGFR are often overexpressed in salivary gland cancer "
                                         f"(SGC), this study evaluated the efficacy and safety of cabozantinib in "
                                         f"recurrent/metastatic (R/M) SGC pts. Methods: A single center, "
                                         f"single arm, phase II study was conducted. Immunohistochemical c-MET "
                                         f"positive (H-score ≥10) R/M SGC pts were included in 3 cohorts\n "
                                         f"Answer:"
                                         f"[{{"
                                         f"'Biomarker': 'c-MET positive',\n"
                                         f"'Target Indication':'salivary gland cancer (SGC)'\n"
                                         f"}}]\n"
                                         f"e.g.3\n"
                                         f"Input:\n"
                                         f"These data, representing PD-L1 and CD8 expression profiles for a "
                                         f"BRAF-mutant MM population in the context of outcomes following D+T, "
                                         f"showed that clinical benefit was maintained regardless of immune "
                                         f"phenotype. The results also suggest that an immune component has an "
                                         f"impact on outcomes following targeted therapy. \n "
                                         f"Answer:"
                                         f"[{{"
                                         f"'Biomarker': 'BRAF-mutant',\n"
                                         f"'Target Indication':'None'\n"
                                         f"}}]\n"
                                         f"e.g.4\n"
                                         f"Input:\n"
                                         f"To date, no biomarker of efficacy of nivolumab+/-ipilimumab (N+/-I) or "
                                         f"anti-VEGFR TKI has been prospectively validated in mRCC. The BIONIKK "
                                         f"trial showed promising objective response rate (ORR) and "
                                         f"progression-free survival (PFS) with these treatments in first line (L1) "
                                         f"after selection by tumour molecular group. We report OS and efficacy "
                                         f"results of the second-line (L2) treatment.  \n "
                                         f"Answer:"
                                         f"[{{"
                                         f"'Biomarker': 'None',\n"
                                         f"'Target Indication': 'mRCC'\n"
                                         f"}}]"
                                         f"e.g.5\n"
                                         f"Input:\n"
                                         f"Tenofovir alafenamide versus tenofovir disoproxil fumarate for the "
                                         f"treatment of HBeAg-positive chronic hepatitis B virus infection: a "
                                         f"randomised, double-blind, phase 3, non-inferiority trial\n "
                                         f"Answer:"
                                         f"[{{"
                                         f"'Biomarker': 'HBeAg-positive',\n"
                                         f"'Target Indication': 'chronic hepatitis B virus'\n"
                                         f"}}]\n"
                                         f"\n\n"
                                         # f"So please tell me the 'Biomarker' in the following paragraph,"
                                         f"Input: \n "
                                         f"{abstract}\n"
                                         f"Answer:")]
    response = ou.chat_completion(message, temperature=0.1, timeout=20)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [(ju.json_extraction(get_evaluation(x))) for x in abstracts]
    # results = [(get_evaluation(x)) for x in abstracts]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))


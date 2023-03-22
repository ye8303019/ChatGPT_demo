import utils.chunk_utils as cu
import utils.openai_utils as ou

token_threshold = 1800
model = "gpt-3.5-turbo"
meeting_abstract = cu.get_file_content("abstract_19", token_threshold, model)


# if only CTGov clinical trials could be listed in the abstract
def gpt_extraction(abstract):
    message = [{"role": "system", "content": "Now you play a role of a excellent clinical trial researcher, you know "
                                             "well about the clinical trials"},
               {"role": "user", "content": f"The list of argument roles corresponding to the event type "
                                           f"[Clinical Trials : R&D status] is ['Identifier', 'Clinical Trial Code', "
                                           f"'Phase', 'Target Indication', 'BioMarker'], "
                                           f"and i will give you a sentence "
                                           f"or paragraph or article, please extract the event arguments according "
                                           f"to the argument roles, and return them in the form of a table."
                                           f"If no argument role has a corresponding argument content, "
                                           f"the argument content returns 'None'.  "
                                           f"Remember some important concepts:\n"
                                           f"1 - there is only one main identifier which is related to the study result "
                                           f"and clinical trial code usually dubbed by "
                                           f"the company itself\n"
                                           f"2 - the enumeration of the 'Phase' could mapping to ["
                                           f"'Early Phase 1', 'Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 2/3', "
                                           f"'Phase 3', 'Phase4']\n"
                                           f"3 - the 'Target Indication' means the disease which "
                                           f"are being studied in the content\n"
                                           f"e.g.1: \n "
                                           f"To report the results of a pre-planned interim analysis of Low-PV, "
                                           f"a Phase I/II "
                                           f"investigator driven randomized trial (NCT030030025) conducted to assess "
                                           f"the "
                                           f"benefit/risk profile of Ropeginterferon alfa-2b versus phlebotomy alone ("
                                           f"standard therapy) in low-risk patients with PV. \n"
                                           f"because Low-PV is refer to Low Pharmacovigilance but not a code\n"
                                           f"Then, the table should looks like: \n "
                                           f"| Identifier | Clinical Trial Code | Phase | Target Indication | BioMarker |\n"
                                           f"| ---- | ---- | ---- | ---- | ---- | ---- |\n"
                                           f"| NCT030030025 | None | Phase 1/2 | None | None |\n"
                                           f"e.g.2:\n"
                                           f"Adjuvant pembrolizumab (pembro) for renal cell carcinoma (RCC) across "
                                           f"UCLA Integrated Staging System (UISS) risk groups and disease stage: "
                                           f"Subgroup analyses from the KEYNOTE-564 study.Background: Adjuvant pembro "
                                           f"prolonged disease-free survival (DFS) for patients (pts) with RCC at "
                                           f"increased risk of recurrence after nephrectomy in the Ph1b "
                                           f"KEYNOTE-564 study (NCT03142334). This post hoc exploratory analysis "
                                           f"evaluated efficacy of adjuvant pembro in pt subgroups based on UISS and "
                                           f"disease stage.Assuming the  0/1 lines of prior therapy ORR of 40%, 40 pts would give a 95% CI with a lower limit of 25% (CI is 0.25 to 0.57) for ORR\n "
                                           f"Then, the table looks like:\n"
                                           f"| Identifier | Clinical Trial Code | Phase | Target Indication | BioMarker |\n"
                                           f"| ---- | ---- | ---- | ---- | ---- | ---- |\n"
                                           f"| NCT03142334 | KEYNOTE-564 | Phase 1b | renal cell carcinoma (RCC) | None |\n"
                                           f"e.g.3:\n"
                                           f"Prognostic stratification by the Meet-URO score in a real-world elderly "
                                           f"population of patients (pts) with metastatic renal cell carcinoma (mRCC) "
                                           f"receiving cabozantinib: A subanalysis of the prospective ZEBRA study ("
                                           f"Meet-URO 9). Further applications of the Meet-URO score in mRCC pts "
                                           f" that previously received ≥2 lines of therapy including a platinum doublet were treated with 4 mg RRx-001 IV once per week. . Clinical trial information: 2018/116/PU.Eligible pts (age ≥18 y) had histologically confirmed, CD20-positive R/R NHL "
                                           f"Then, the table looks like:\n"
                                           f"| Identifier | Clinical Trial Code | Phase | Target Indication | BioMarker |\n"
                                           f"| ---- | ---- | ---- | ---- | ---- | ---- |\n"
                                           f"| 2018/116/PU | ZEBRA | None | metastatic renal cell carcinoma (mRCC) | CD20-positive |\n"
                                           f"\n"
                                           f"e.g.4:\n"
                                           f"205P - Pooled exploratory analysis of survival in patients (pts) with HR+/HER2- advanced breast cancer (ABC) and visceral metastases (mets) treated with ribociclib (RIB) + endocrine therapy (ET) in the MONALEESA (ML) trials. Clinical trial identification"
                                           f" NCT01958021 (ML-2) NCT02422615 (ML-3) NCT02278120 (ML-7)."
                                           f"Then, the table looks like:\n"
                                           f"| Identifier | Clinical Trial Code | Phase | Target Indication | BioMarker |\n"
                                           f"| ---- | ---- | ---- | ---- | ---- | ---- |\n"
                                           f"| NCT01958021 | ML-2 | None | HR+/HER2- advanced breast cancer (ABC)  | HR+/HER2- |\n"
                                           f"| NCT02422615 | ML-3 | None | HR+/HER2- advanced breast cancer (ABC)  | HR+/HER2- |\n"
                                           f"| NCT02278120 | ML-7 | None | HR+/HER2- advanced breast cancer (ABC)  | HR+/HER2- |\n"
                                           f"\n"
                                           f"Now, use this rule to extract the event from the content below : \n "
                                           f"{abstract}"
                }]
    return ou.chat_completion(message, temperature=0.6)


[print(gpt_extraction(x)) for x in meeting_abstract]

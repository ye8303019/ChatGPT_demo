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
                                           f"[Clinical Trials : Clinical Trial Code] is ['Identifier','Clinical "
                                           f"Trial Code'], "
                                           f"and I will give you a sentence "
                                           f"or paragraph or article, please extract the event arguments according "
                                           f"to the argument roles, and return them in the form of a json schema like "
                                           f"below. "
                                           f"If no argument role has a corresponding argument content, "
                                           f"the argument content returns 'None'.  "
                                           f"[{{"
                                           f"'Identifier': String,\n"
                                           f"'Clinical Trial Code': String\n"
                                           f"}}]"
                                           f"Remember the key concepts below:"
                                           f"1 - The 'Clinical Trial Code' usually dubbed by the company itself, "
                                           f"used to "
                                           f"named a clinical trial before it's been register\n "
                                           f"2 - The 'Clinical Trial Code' is not the identifier, for example, "
                                           f"it's not NCTXXXX,ISRCTNXXXX,ChiCTRXXXX\n "
                                           f"e.g.1: \n "
                                           f"Phase 2 study of the efficacy and safety of erdafitinib in patients ("
                                           f"pts) with intermediate-risk non–muscle-invasive bladder cancer ("
                                           f"IR-NMIBC) with FGFR3/2 alterations (alt) in THOR-2: Cohort 3 interim "
                                           f"analysis. \n"
                                           f"Background: Current treatments (tx) of papillary NMIBC are not "
                                           f"selective. THOR-2 (NCT04172675) is a "
                                           f"multicohort phase 2 study of erda in pts with NMIBC. We report results "
                                           f"in an exploratory cohort of pts with IR-NMIBC with FGFRalt (Cohort 3). "
                                           f"Methods: Inclusion: age ≥18 y, with histologically confirmed NMIBC with "
                                           f"FGFR3/2alt (local/central testing) and recurrent IR disease, "
                                           f"with all previous tumors being low grade (Gr) (Gr 1-2), Ta/T1, "
                                           f"no previous carcinoma in situ, risk of progression <5% in the next 2 y, "
                                           f"and risk of recurrence >50%. All tumors were removed by transurethral "
                                           f"resection of bladder tumor except for a marker lesion (single untouched "
                                           f"5-10 mm lesion).  No pts had tx-related serious TEAEs or tx-related "
                                           f"TEAEs leading to discontinuation. No deaths occurred. Conclusions: Data "
                                           f"from Cohort 3 of THOR-2 demonstrate efficacy in adult pts with IR-NMIBC "
                                           f"with FGFRalt. Safety data were consistent with the known safety profile "
                                           f"of erda. Clinical trial information: NCT04172675.\n "
                                           f"Then, the json should looks like: \n "
                                           f"[{{"
                                           f"'Identifier': 'NCT04172675',\n"
                                           f"'Clinical Trial Code': 'THOR-2'\n"
                                           f"}}]"
                                           f"e.g.2:\n"
                                           f"Background: \n"
                                           f"RIB + ET demonstrated statistically significant progression-free "
                                           f"survival (PFS) and overall survival (OS) benefits in the ML-2, -3, "
                                           f"and -7 trials in pts with HR+/HER2− ABC. The presence of visceral mets "
                                           f"indicates a worse prognosis, with a particularly poor survival observed "
                                           f"in pts with liver mets. Here we report a pooled survival analysis of the "
                                           f"ML-2, -3, and -7 trials in pts with visceral mets, including those with "
                                           f"liver mets.Methods In ML-2, postmenopausal pts were randomized 1:1 to "
                                           f"receive first-line (1L) RIB or placebo (PBO) with letrozole. In ML-3, "
                                           f"postmenopausal pts were randomized 2:1 to receive RIB or PBO with "
                                           f"fulvestrant in the 1L or second-line (2L) setting. In ML-7, "
                                           f"premenopausal pts were randomized 1:1 to receive 1L RIB or PBO and "
                                           f"goserelin with nonsteroidal aromatase inhibitor (NSAI)/tamoxifen (only "
                                           f"pts in the NSAI arm were included in this analysis). \n"
                                           f"Clinical trial identification \n "
                                           f"NCT01958021 (ML-2) NCT02422615 (ML-3) NCT02278120 (ML-7). "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': 'NCT01958021',\n"
                                           f"'Clinical Trial Code': 'ML-2'\n "
                                           f"}},{{"
                                           f"'Identifier': 'NCT02422615',\n"
                                           f"'Clinical Trial Code': 'ML-3'\n "
                                           f"}},{{"
                                           f"'Identifier': 'NCT02278120',\n"
                                           f"'Clinical Trial Code': 'ML-7'\n "
                                           f"}}]"
                                           f"e.g.4:\n"
                                           f"Cabozantinib in combination with atezolizumab in non-clear cell renal "
                                           f"cell carcinoma: Extended follow-up results of cohort 10 of the "
                                           f"study(COSMIC-021).\n"
                                           f"Background: \n"
                                           f"In the COSMIC-021 phase 1b study ("
                                           f"NCT03170960) evaluating cabozantinib plus atezolizumab in advanced solid "
                                           f"tumors, this combination therapy demonstrated encouraging clinical "
                                           f"activity in patients with advanced non-clear cell renal cell carcinoma ("
                                           f"nccRCC) with a median follow-up of 13 mo (Pal. JCO 2021). "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': 'None',\n"
                                           f"'Clinical Trial Code': 'COSMIC-021'\n "
                                           f"}}]"
                                           f"e.g.5:\n"
                                           f"Trifluridine/tipiracil plus bevacizumab for third-line treatment of "
                                           f"refractory metastatic colorectal cancer: The phase 3 randomized SUNLIGHT "
                                           f"study.\n "
                                           f"Background: \n"
                                           f"Trifluridine/tipiracil (FTD/TPI) plus bevacizumab (Bev) demonstrated "
                                           f"promising efficacy in a randomized phase 2 trial of heavily pretreated "
                                           f"patients (pts) with metastatic colorectal cancer (mCRC). SUNLIGHT was "
                                           f"conducted to confirm these findings. \n"
                                           f"Methods: \n"
                                           f"The global phase 3 "
                                           f"SUNLIGHT study enrolled pts aged ≥18 years with histologically confirmed "
                                           f"mCRC, ECOG PS 0/1, and treated with 1-2 prior chemotherapy regimens in "
                                           f"an advanced setting, including fluoropyrimidines, irinotecan, "
                                           f"oxaliplatin, an anti-VEGF monoclonal antibody (if medically considered) "
                                           f"and/or anti-EGFR monoclonal antibody for RAS wild-type tumors. Pts were "
                                           f"randomised (1:1) to receive FTD/TPI (35 mg/m2 twice daily on days 1–5 "
                                           f"and 8–12 of each 28-day cycle) alone or combined with Bev (5 mg/kg on "
                                           f"days 1 and 15). Primary endpoint was overall survival (OS). \n "
                                           f"Then, the json looks like:\n"
                                           f"[{{"
                                           f"'Identifier': 'None',\n"
                                           f"'Clinical Trial Code': 'SUNLIGHT'\n "
                                           f"}}]"
                                           f"Now, use this rule to extract the event from the content below : \n "
                                           f"{abstract}"
                }]
    response = ou.chat_completion(message, temperature=0.0, timeout=20)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [(ju.json_extraction(gpt_extraction(x))) for x in abstracts]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))




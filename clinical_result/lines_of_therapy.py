import utils.chunk_utils as cu
import utils.openai_utils as ou
import utils.json_utils as ju
import main

token_threshold = 1300
model = main.OPENAI_CHAT_MODEL
key_words = ['line', 'lines', 'prior', 'untreated']


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
        dicts.append({"Line of Therapy": "None"})
    return dicts


# if only CTGov clinical trials could be listed in the abstract
def gpt_extraction(abstract):
    abstract = abstract.replace("\"", " ").replace("'", " ").replace("[", " ").replace("]", " ")
    message = [{"role": "system", "content": "Now you are a excellent NLP Classification model"},
               {"role": "user", "content": f"Knowledge:\n"
                                           f"1. First Line Therapy(Frontline Therapy)\n"
                                           f"The first treatment given for a disease. It is often part of a standard set of treatments, such as surgery followed by chemotherapy and radiation. When used by itself, first-line therapy is the one accepted as the best treatment. If it doesn’t cure the disease or it causes severe side effects, other treatment may be added or used instead. Also called induction therapy, primary therapy, and primary treatment.\n"
                                           f"2. Second Line Therapy\n"
                                           f"Treatment that is given when initial treatment (first-line therapy) doesn’t work, or stops working.Second-line therapy may involve a different type of drug or combination of drugs than first-line therapy.\n"
                                           f"3. Third Line Therapy\n"
                                           f"Treatment that is given when both initial treatment (first-line therapy) and subsequent treatment (second-line therapy) don’t work, or stop working. \n"
                                           f"4. Last Line Therapy (Salvage Therapy)\n"
                                           f"Treatment that is given when all of the initial treatment (first-line therapy), subsequent treatment (second-line therapy) and third-line therapy and even more lines of therapy don't work, or stop working. \n"
                                           f"5. Maintenance Therapy\n"
                                           f"This is the treatment given to patients after they have achieved remission to prevent relapse or progression of the disease.\n"
                                           f"6. Adjuvant Therapy\n"
                                           f"This is the treatment given to patients after surgery to reduce the risk of recurrence or spread of the disease.\n"
                                           f"7. Neoadjuvant Therapy\n"
                                           f"This is the treatment given to patients before surgery to shrink the size of the tumor or make it easier to remove.\n"
                                           f"8. Palliative Therapy\n"
                                           f"This is the treatment given to patients to relieve symptoms and improve quality of life, rather than to cure the disease. Palliative therapy is often used in patients with advanced or incurable cancer\n"
                                           f"\n"
                                           f"Rules:"
                                           f"1. All the answer should only in the scope of the knowledge provided above, don't reply the answer out of the scope\n"
                                           f"2. You can get the answer ONLY when the content EXPLICITLY INCLUDE some key words like 'untreated','prior', 'line', 'lines', 'Salvage', 'Maintenance', 'Adjuvant', 'Neoadjuvant', 'Palliative', otherwise, you are not 100% confident so you can't tell which line of therapy it is\n"
                                           f"\n\n"
                                           f"Examples:\n"
                                           f"Input:\n"
                                           f"Approximately 40% of patients (pts) with non-Hodgkin lymphoma (NHL) have disease that will relapse or is refractory to chemotherapy and/or immunotherapies; management of these pts remains a challenge. Although follicular lymphoma (FL) generally responds well to first-line treatment (tx), this disease is characterized by frequent relapses with shorter intervals between tx lines.\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json: \n"
                                           f"[{{'Line of Therapy':'Second Line Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'Although follicular lymphoma (FL) generally responds well to first-line treatment (tx)', and the subsequent sentence did not specify the line of therapy, so the answer is : 'Second Line Therapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Neratinib Plus Capecitabine Versus Lapatinib Plus Capecitabine in HER2-Positive Metastatic Breast Cancer Previously Treated With ≥ 2 HER2-Directed Regimens: Phase III NALA Trial.\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json: \n"
                                           f"[{{'Line of Therapy':'Third Line Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'Treated With ≥ 2', and the subsequent sentence did not specify the line of therapy, so the answer is : 'Third Line Therapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"In the PAOLA-1/ENGOT-ov25 (NCT02477644) primary analysis, adding ola to maintenance bev after first-line (1L) platinum-based chemotherapy (PBC) + bev led to a significant progression-free survival (PFS) benefit in AOC (HR 0.59, 95% CI 0.49–0.72; P<0.001), particularly in pts with homologous recombination deficiency (HRD+; BRCA1/2 mutation [BRCAm] and/or genomic instability; Ray-Coquard et al NEJM 2019). Here, we report the prespecified final OS analysis. Conclusions: Despite a high proportion of pts in the control arm receiving a PARP inhibitor post-progression, ola + bev provided a clinically meaningful improvement in OS for 1L HRD+ pts with and without a tBRCAm, confirming ola + bev as standard of care in this setting.\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'Maintenance Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'after first-line (1L) platinum-based chemotherapy (PBC) + bev led to a significant progression-free survival (PFS) benefit in AOC', the 'after' is key to the judge, and also mentioned 'ola + bev provided a clinically meaningful improvement in OS for 1L HRD+ pts with and without a tBRCAm', combine 2 sentence together, which means after first line treatment, the current treatment could prevent relapse or progression of the disease after they achieved remission, and the subsequent sentence did not specify the line of therapy, so the answer is : 'Maintenance therapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"IAvelumab (anti-PD-L1) as first-line switch-maintenance or second-line therapy in patients with advanced gastric or gastroesophageal junction cancer: phase 1b results from the JAVELIN Solid Tumor trial.\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'Maintenance Therapy'}},{{'Line of Therapy':'Second Line Threrapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'as first-line switch-maintenance or second-line', here author mentioned 'or', which means after first line therapy, the author think the treatment could be maintenance therapy or second line therapy, so the answer is : 'Maintenance Therapy' and 'Second Line Threrapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"1533P - Atezolizumab (ATZ) plus carboplatin (Cb) and etoposide (eto) in patients with untreated extensive-stage small cell lung cancer (ES-SCLC): Results from the interim analysis of MAURIS trial\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'First Line Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the author mentioned that 'etoposide (eto) in patients with untreated extensive-stage small cell lung cancer', the 'untreated' is the key, it's means the patient never get any treatment, at this point, it's should be 'First Line Therapy' so the answer is : 'Maintenance Therapy' and 'Second Line Threrapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"FUMANBA-1 is a phase 1b/2 study of CT103A that is conducted in 14 centers in China. This study enrolled RRMM subjects who received ≥ 3 lines of prior therapies containing at least a proteasome inhibitor and an immunomodulatory agent and were refractory to their last line of treatment\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'Last Line Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the author mentioned that 'who received ≥ 3 lines of prior therapies', which means these patients receive more than 3 lines of therapy before, it's totally match the definition of 'Last line therapy (Salvage therapy)', so the answer is : 'Maintenance Therapy' and 'Second Line Threrapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Ibrutinib (I) plus bendamustine and rituximab (BR) in previously treated chronic lymphocytic leukemia/small lymphocytic lymphoma (CLL/SLL): a 2-year follow-up of the HELIOS study.\n"
                                           f"Q:What's the line of therapy for the input? \n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'None'}}]\n"
                                           f"Reason:\n"
                                           f"Because although the content mentioned 'previously treated chronic lymphocytic leukemia/small lymphocytic lymphoma (CLL/SLL)' but there is no more information about 'previously' line belong to which line of therapy, so the answer is 'None'.\n"
                                           f"\n"
                                           f"Based on the knowledge and rules provided above, please get answer for the input below:\n"
                                           f"Input:\n"
                                           f"{abstract}\n"
                                           f"\n"
                                           f"Based on the knowledge and rules above, REMEMBER, IF THE CONTENT NOT EXLICITLY CONTAIN 'untreated','prior', 'line', 'lines', 'Salvage', 'Maintenance', 'Adjuvant', 'Neoadjuvant', 'Palliative', then you are not 100% sure, so tell me the line of therapy for the therapeutic regimen studied for the input? If you don't know or not sure, return 'None' in the field 'Line of Therapy' in json\n"
                                           f"A:"}]
    response = ou.chat_completion(message, temperature=0.2, timeout=25)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [ju.json_extraction(gpt_extraction(abstracts[0]))]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))

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
    if len(dicts) == 0:
        dicts.append({"Line of Therapy": "None"})
    return dicts


# if only CTGov clinical trials could be listed in the abstract
def gpt_extraction(abstract):
    abstract = abstract.replace("\"", " ").replace("'", " ")
    message = [{"role": "system", "content": "Now you are a excellent NLP Classification model"},
               {"role": "user", "content": f"Knowledge:\n"
                                           f"1. First line therapy(frontline therapy)\n"
                                           f"The first treatment given for a disease. It is often part of a standard set of treatments, such as surgery followed by chemotherapy and radiation. When used by itself, first-line therapy is the one accepted as the best treatment. If it doesn’t cure the disease or it causes severe side effects, other treatment may be added or used instead. Also called induction therapy, primary therapy, and primary treatment.\n"
                                           f"2. Second line therapy\n"
                                           f"Treatment that is given when initial treatment (first-line therapy) doesn’t work, or stops working.Second-line therapy may involve a different type of drug or combination of drugs than first-line therapy.\n"
                                           f"3. Third line therapy\n"
                                           f"Treatment that is given when both initial treatment (first-line therapy) and subsequent treatment (second-line therapy) don’t work, or stop working. \n"
                                           f"4. Maintenance therapy\n"
                                           f"This is the treatment given to patients after they have achieved remission to prevent relapse or progression of the disease.\n"
                                           f"5. Adjuvant therapy\n"
                                           f"This is the treatment given to patients after surgery to reduce the risk of recurrence or spread of the disease.\n"
                                           f"6. Neoadjuvant therapy\n"
                                           f"This is the treatment given to patients before surgery to shrink the size of the tumor or make it easier to remove.\n"
                                           f"7. Palliative therapy\n"
                                           f"This is the treatment given to patients to relieve symptoms and improve quality of life, rather than to cure the disease. Palliative therapy is often used in patients with advanced or incurable cancer\n"
                                           f"\n"
                                           f"Based on the knowledge provided above, the answer should only in these 7 types of therapy, so here are some examples:\n"
                                           f"Input:\n"
                                           f"Approximately 40% of patients (pts) with non-Hodgkin lymphoma (NHL) have disease that will relapse or is refractory to chemotherapy and/or immunotherapies; management of these pts remains a challenge. Although follicular lymphoma (FL) generally responds well to first-line treatment (tx), this disease is characterized by frequent relapses with shorter intervals between tx lines.\n"
                                           f"Q:What's the line of therapy most likely for the input? If you don't know, return 'None' in the field 'Line of Therapy' in json\n"
                                           f"A: \n"
                                           f"Json: \n"
                                           f"[{{'Line of Therapy':'Second Line Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'Although follicular lymphoma (FL) generally responds well to first-line treatment (tx)', and the subsequent sentence did not specify the line of therapy, so the answer is : 'Second Line Therapy'.\n"
                                           f"\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"Neratinib Plus Capecitabine Versus Lapatinib Plus Capecitabine in HER2-Positive Metastatic Breast Cancer Previously Treated With ≥ 2 HER2-Directed Regimens: Phase III NALA Trial.\n"
                                           f"Q:What's the line of therapy most likely for the input? If you don't know, return 'None' in the field 'Line of Therapy' in json\n"
                                           f"A: \n"
                                           f"Json: \n"
                                           f"[{{'Line of Therapy':'Third Line Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'Treated With ≥ 2', and the subsequent sentence did not specify the line of therapy, so the answer is : 'Third Line Therapy'.\n"
                                           f"\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"In the PAOLA-1/ENGOT-ov25 (NCT02477644) primary analysis, adding ola to maintenance bev after first-line (1L) platinum-based chemotherapy (PBC) + bev led to a significant progression-free survival (PFS) benefit in AOC (HR 0.59, 95% CI 0.49–0.72; P<0.001), particularly in pts with homologous recombination deficiency (HRD+; BRCA1/2 mutation [BRCAm] and/or genomic instability; Ray-Coquard et al NEJM 2019). Here, we report the prespecified final OS analysis. Conclusions: Despite a high proportion of pts in the control arm receiving a PARP inhibitor post-progression, ola + bev provided a clinically meaningful improvement in OS for 1L HRD+ pts with and without a tBRCAm, confirming ola + bev as standard of care in this setting.\n"
                                           f"Q:What's the line of therapy most likely for the input? If you don't know, return 'None' in the field 'Line of Therapy' in json\n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'Maintenance Therapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'after first-line (1L) platinum-based chemotherapy (PBC) + bev led to a significant progression-free survival (PFS) benefit in AOC', the 'after' is key to the judge, and also mentioned 'ola + bev provided a clinically meaningful improvement in OS for 1L HRD+ pts with and without a tBRCAm', combine 2 sentence together, which means after first line treatment, the current treatment could prevent relapse or progression of the disease after they achieved remission, and the subsequent sentence did not specify the line of therapy, so the answer is : 'Maintenance therapy'.\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"IAvelumab (anti-PD-L1) as first-line switch-maintenance or second-line therapy in patients with advanced gastric or gastroesophageal junction cancer: phase 1b results from the JAVELIN Solid Tumor trial.\n"
                                           f"Q:What's the line of therapy most likely for the input? If you don't know, return 'None' in the field 'Line of Therapy' in json\n"
                                           f"A: \n"
                                           f"Json:\n"
                                           f"[{{'Line of Therapy':'Maintenance Therapy'}},{{'Line of Therapy':'Second Line Threrapy'}}]\n"
                                           f"Reason:\n"
                                           f"Because the content mentioned 'as first-line switch-maintenance or second-line', here author mentioned 'or', which means after first line therapy, the author think the treatment could be maintenance therapy or second line therapy, so the answer is : 'Maintenance Therapy' and 'Second line threrapy'.\n"
                                           f"\n"
                                           f"\n"
                                           f"Input:\n"
                                           f"{abstract}\n"
                                           f"\n"
                                           f"Q:What's the line of therapy that you have 100% confidence about for the input? If you don't know or not sure, return 'None' in the field 'Line of Therapy' in json\n"
                                           f"A:"}]
    response = ou.chat_completion(message, temperature=0.9, timeout=25)
    print(response)
    return response


def get_final_result(abstract):
    abstracts = cu.get_file_contents(abstract, token_threshold, model)
    results = [ju.json_extraction(gpt_extraction(abstracts[0]))]
    return format_answer(results)


if __name__ == '__main__':
    print(ju.json_beautify(get_final_result(cu.get_file_content("data/tmp_test_data_1"))))

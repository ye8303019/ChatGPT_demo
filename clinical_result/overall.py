import identifier_phase, biomarker, clinical_trial_code, patient_number, lines_of_therapy, study_evaluation
import utils.chunk_utils as cu
import utils.json_utils as ju


def get_overall_info(content):
    overall_dict = {}
    identifier_phase_dicts = identifier_phase.get_final_result(content)
    overall_dict['Identifier'] = ','.join([d['Identifier'] for d in identifier_phase_dicts])
    overall_dict['Phase'] = ','.join([d['Phase'] for d in identifier_phase_dicts])
    overall_dict['Drug'] = ','.join([d['Drug'] for d in identifier_phase_dicts])
    clinical_trial_code_dicts = clinical_trial_code.get_final_result(content)
    overall_dict['Clinical Trial Code'] = ','.join([d['Clinical Trial Code'] for d in clinical_trial_code_dicts])
    biomarker_dicts = biomarker.get_final_result(content)
    overall_dict['Biomarker'] = ','.join([d['Biomarker'] for d in biomarker_dicts])
    # target_indication_dicts = target_indication.get_final_result(content)
    overall_dict['Target Indication'] = ','.join([d['Target Indication'] for d in biomarker_dicts])
    patient_number_dicts = patient_number.get_final_result(content)
    overall_dict['Overall Enrollment'] = ','.join([d['Overall Enrollment'] for d in patient_number_dicts])
    lines_of_therapy_dicts = lines_of_therapy.get_final_result(content)
    overall_dict['Line of Therapy'] = ','.join([d['Line of Therapy'] for d in lines_of_therapy_dicts])
    study_evaluation_dicts = study_evaluation.get_final_result(content)
    overall_dict['Overall Evaluation'] = ','.join([d['Evaluation'] for d in study_evaluation_dicts])
    print()
    print("============================   Overall Result  =============================")
    return overall_dict


if __name__ == '__main__':
    print(ju.json_beautify(get_overall_info(cu.get_file_content("data/tmp_test_data_1"))))

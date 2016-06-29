#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import unittest
import sys
import json
sys.path.append('../')
from request2doc import DictMixer


class ParserTestCase(unittest.TestCase):
    def test_dict_mixer(self):
        data = '''
        {
            "success": true,
            "data": {
                "results": [
                    {
                        "date": "2016-06-27 周一",
                        "homeworks": [
                            {
                                "_id": "5770e55880adb9443c8b4c99",
                                "subject_id": 3,
                                "teacher_id": 126685,
                                "book_id": "BK_20300001479700",
                                "subtitle": "期末复习",
                                "tags": [
                                    "final"
                                ],
                                "expect_duration": 2238,
                                "include_subjective": 1,
                                "name": "普通作业123",
                                "paper_id": "PM_20300004319915",
                                "type": 3,
                                "create_time": 1467016536840,
                                "clazz_id": 12941,
                                "real_clazz_id": 33721224,
                                "status": 0,
                                "start_time": 1467016536706,
                                "close_time": 1467215940706,
                                "open_answer_time": null,
                                "clazz_name": "七年级2班",
                                "student_count": 4,
                                "start_time_str": "6-27 16:35",
                                "close_time_str": "6-29 23:59",
                                "is_overtime": 0,
                                "is_all_student_finished": 0,
                                "is_all_corrected": 1,
                                "is_comment_setted": 0,
                                "finished_count": 1,
                                "wait_crt_count": 0,
                                "wait_view_count": 0,
                                "crt_count": 0,
                                "avg_score": 0,
                                "enable_check": false,
                                "download_url": "/teacher/homework/downloadPaper?homework_id=5770e55880adb9443c8b4c99",
                                "redo_assign_status": 1,
                                "question_type_info": "听力选择题(2)、选择题(2)、写作(2)",
                                "redo_button_status": 0,
                                "redo_homework": ""
                            },
                            {
                                "_id": "5770aa4d80adb950378b4c6d",
                                "subject_id": 3,
                                "teacher_id": 126685,
                                "book_id": "BK_20300001479700",
                                "subtitle": "Unit 1 Can you play the guitar?",
                                "tags": [],
                                "expect_duration": 240,
                                "include_subjective": 0,
                                "name": "单词和例句",
                                "paper_id": "PM_20300004317793",
                                "type": 3,
                                "create_time": 1467001421412,
                                "clazz_id": 12941,
                                "real_clazz_id": 33721224,
                                "status": 0,
                                "start_time": 1467001421207,
                                "close_time": 1467215940207,
                                "open_answer_time": null,
                                "clazz_name": "七年级2班",
                                "student_count": 4,
                                "start_time_str": "6-27 12:23",
                                "close_time_str": "6-29 23:59",
                                "is_overtime": 0,
                                "is_all_student_finished": 0,
                                "is_all_corrected": 1,
                                "is_comment_setted": 0,
                                "finished_count": 1,
                                "wait_crt_count": 0,
                                "wait_view_count": 1,
                                "crt_count": 0,
                                "avg_score": 67,
                                "enable_check": false,
                                "download_url": "",
                                "redo_assign_status": 1,
                                "question_type_info": "词汇练习(12)",
                                "redo_button_status": 0,
                                "redo_homework": ""
                            },
                            {
                                "_id": "5770a85880adb9de378b4c73",
                                "subject_id": 3,
                                "teacher_id": 126685,
                                "book_id": "BK_20300001479700",
                                "subtitle": "Unit 1 Can you play the guitar?",
                                "tags": [],
                                "expect_duration": 90,
                                "include_subjective": 0,
                                "name": "单词词汇",
                                "paper_id": "PM_20300004316431",
                                "type": 3,
                                "create_time": 1467000920886,
                                "clazz_id": 12941,
                                "real_clazz_id": 33721224,
                                "status": 0,
                                "start_time": 1467000920685,
                                "close_time": 1467215940685,
                                "open_answer_time": null,
                                "clazz_name": "七年级2班",
                                "student_count": 4,
                                "start_time_str": "6-27 12:15",
                                "close_time_str": "6-29 23:59",
                                "is_overtime": 0,
                                "is_all_student_finished": 0,
                                "is_all_corrected": 1,
                                "is_comment_setted": 0,
                                "finished_count": 1,
                                "wait_crt_count": 0,
                                "wait_view_count": 1,
                                "crt_count": 0,
                                "avg_score": 33,
                                "enable_check": false,
                                "download_url": "",
                                "redo_assign_status": 1,
                                "question_type_info": "词汇练习(6)",
                                "redo_button_status": 0,
                                "redo_homework": ""
                            }
                        ]
                    },
                    {
                        "date": "2016-06-17",
                        "homeworks": [
                            {
                                "_id": "57635d54ad73936409000045",
                                "subject_id": 3,
                                "teacher_id": 126685,
                                "book_id": "BK_20300001481320",
                                "subtitle": "Unit 10 I've had this bike for three years.",
                                "tags": [],
                                "expect_duration": 40,
                                "include_subjective": 0,
                                "name": "英语作业 06-17",
                                "paper_id": "PM_20300003735270",
                                "type": 3,
                                "create_time": 1466129712000,
                                "clazz_id": 10949,
                                "real_clazz_id": 829966,
                                "status": 5,
                                "start_time": 1466129665000,
                                "close_time": 1466351940000,
                                "open_answer_time": null,
                                "clazz_name": "六年级1班",
                                "student_count": 4,
                                "start_time_str": "6-17 10:14",
                                "close_time_str": "6-19 23:59",
                                "is_overtime": 1,
                                "is_all_student_finished": 0,
                                "is_all_corrected": 1,
                                "is_comment_setted": 0,
                                "finished_count": 0,
                                "wait_crt_count": 0,
                                "wait_view_count": 0,
                                "crt_count": 0,
                                "avg_score": 0,
                                "enable_check": false,
                                "download_url": "/teacher/homework/downloadPaper?homework_id=57635d54ad73936409000045",
                                "redo_assign_status": 2,
                                "question_type_info": "选择题(1)",
                                "redo_button_status": 0,
                                "redo_homework": ""
                            }
                        ]
                    }
                ],
                "total_items": 64,
                "total_pages": 4,
                "current_page": 1,
                "page_size": 20
            },
            "message": "",
            "error_code": 0
        }
        '''
        dic = json.loads(data)
        mixer = DictMixer(dic)
        result = mixer.expand_item_list()
        print result

        # self.assertEqual(result[0].full_key(), 'a.b.0')
        # self.assertEqual(result[1].full_key(), 'a.b.1.e')
        # self.assertEqual(result[2].full_key(), 'a.b.1.d')
        # self.assertEqual(result[3].full_key(), 'a.b1.0')

        mixer.replace_similar_items_route()
        mixer.merge_items()
        print mixer.expand_item_list()

if __name__ == '__main__':
    unittest.main()

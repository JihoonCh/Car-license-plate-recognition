# -*- coding: utf-8 -*-

import os
import requests

# API 키 (발급받은 API 키를 여기에 입력)
api_key = "your-api-key"

# 이미지 폴더 경로 및 파일 리스트 (우분투 환경에 맞게 설정)
image_folder = '/home/jhchoi/Downloads/car_image'
image_files = ['1-1.jpg', '1-2.jpg', '1-3.jpg', '2-1.jpg', '2-2.jpg', '2-3.jpg', '2-4.jpg', '정면1.jpg', '정면2.jpg'
, '00.jpg', '01.jpg', '02.jpg', '03.jpg', '04.jpg',
               '05.jpg', '06.jpg', '07.jpg', '08.jpg', '09.jpg',
               '10.jpg', '11.jpg', '12.jpg', '13.jpg', '14.jpg']

# 각 이미지 파일에 절대 경로를 추가
image_paths = [os.path.join(image_folder, image_file) for image_file in image_files]

# SK Open API의 차량 번호판 인식 엔드포인트 URL
url = "https://apis.openapi.sk.com/sigmeta/lpr/v1"

# 한글 자모를 결합하는 함수 (이미 변환된 자모에 대해선 적용하지 않음)
def combine_jamos(cho, jung):
    cho_map = {
        'ㄱ': 0, 'ㄲ': 1, 'ㄴ': 2, 'ㄷ': 3, 'ㄸ': 4, 'ㄹ': 5, 'ㅁ': 6, 'ㅂ': 7, 'ㅃ': 8,
        'ㅅ': 9, 'ㅆ': 10, 'ㅇ': 11, 'ㅈ': 12, 'ㅉ': 13, 'ㅊ': 14, 'ㅋ': 15, 'ㅌ': 16, 'ㅍ': 17, 'ㅎ': 18
    }
    jung_map = {
        'ㅏ': 0, 'ㅐ': 1, 'ㅑ': 2, 'ㅒ': 3, 'ㅓ': 4, 'ㅔ': 5, 'ㅕ': 6, 'ㅖ': 7, 'ㅗ': 8,
        'ㅘ': 9, 'ㅙ': 10, 'ㅚ': 11, 'ㅛ': 12, 'ㅜ': 13, 'ㅝ': 14, 'ㅞ': 15, 'ㅟ': 16, 'ㅠ': 17,
        'ㅡ': 18, 'ㅢ': 19, 'ㅣ': 20
    }

    if cho in cho_map and jung in jung_map:
        cho_index = cho_map[cho]
        jung_index = jung_map[jung]

        return chr(0xAC00 + (cho_index * 21 + jung_index) * 28)
    else:
        raise ValueError(f"Invalid cho or jung: cho={cho}, jung={jung}")

# 영문 두 글자를 한글 한 글자로 변환하는 함수
def convert_eng_pair_to_kor(pair):
    consonant_map = {
        'b': 'ㅂ', 'c': 'ㄱ', 'd': 'ㄷ', 'f': 'ㅍ', 'g': 'ㄱ',
        'h': 'ㅎ', 'j': 'ㅈ', 'k': 'ㅋ', 'l': 'ㄹ', 'm': 'ㅁ',
        'n': 'ㄴ', 'p': 'ㅍ', 'q': 'ㅋ', 'r': 'ㄹ', 's': 'ㅅ',
        't': 'ㅌ', 'v': 'ㅂ', 'w': 'ㅂ', 'x': 'ㅅ', 'y': 'ㅇ',
        'z': 'ㅈ'
    }

    vowel_map = {
        'a': 'ㅏ', 'e': 'ㅔ', 'i': 'ㅣ', 'o': 'ㅗ', 'u': 'ㅜ'
    }

    if len(pair) == 3 and pair[1:].lower() == 'eo':
        cho = consonant_map.get(pair[0].lower())
        if cho:
            return combine_jamos(cho, 'ㅓ')
    elif len(pair) == 2:
        first, second = pair[0].lower(), pair[1].lower()
        cho = consonant_map.get(first)
        jung = vowel_map.get(second)
        if cho and jung:
            return combine_jamos(cho, jung)
    return pair

# 차량 번호에서 영어 두 글자를 한글 한 글자로 변환하는 함수
def convert_license_plate(lp_string):
    result = []
    i = 0
    while i < len(lp_string):
        if i + 2 < len(lp_string) and lp_string[i].isalpha() and lp_string[i+1:i+3].lower() == 'eo':
            result.append(convert_eng_pair_to_kor(lp_string[i:i+3]))
            i += 3
        elif i + 1 < len(lp_string) and lp_string[i:i+2].lower() == 'eo':
            result.append('어')
            i += 2
        elif lp_string[i].isalpha() and lp_string[i].lower() == 'o':
            result.append('오')
            i += 1
        elif i + 1 < len(lp_string) and lp_string[i].isalpha() and lp_string[i+1].isalpha():
            result.append(convert_eng_pair_to_kor(lp_string[i:i+2]))
            i += 2
        else:
            result.append(lp_string[i])
            i += 1
    return ''.join(result)

# 여러 이미지 파일을 처리하는 함수
def process_images(image_paths):
    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"이미지 파일: {image_path} - 파일을 찾을 수 없습니다.")
            continue

        with open(image_path, "rb") as image_file:
            files = {
                "File": image_file,
            }

            headers = {
                "Accept": "application/json",
                "appKey": api_key
            }

            response = requests.post(url, headers=headers, files=files)

            if response.status_code == 200:
                result = response.json()
                try:
                    lp_string = result['result']['objects'][0]['lp_string']
                    print(f"이미지 파일: {image_path}")
                    converted_lp_string = convert_license_plate(lp_string)
                    print(f"변환된 차량 번호: {converted_lp_string}\n")
                except KeyError:
                    print(f"이미지 파일: {image_path} - 차량 번호를 찾을 수 없습니다.\n")
            else:
                print(f"이미지 파일: {image_path} - API 요청 실패. 상태 코드: {response.status_code}\n")
                print(f"응답 메시지: {response.text}\n")

# 여러 이미지 파일 처리 실행
process_images(image_paths)

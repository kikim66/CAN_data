""" 
 이 프로그램은 , "OK1 + VSTD CAN Protocol-2024.08.29.dbc" 파일을 읽어, cvs file 포맷으로 만들어주는 프로그램이며,
 cvs format으로 변환할 때, 중복된 can message는 한개만 남기고 나머지는 제거하여 중복되지 않게 한다.

  사용법: 
    python3 conv.py

"""
import canmatrix.formats
import csv
import re

def extract_ids_from_dbc(dbc_file):
    """
    DBC 파일에서 BO_ 라인으로부터 메시지 ID를 직접 추출합니다.
    """
    message_ids = {}
    # 파일을 'ISO-8859-1' 인코딩으로 읽습니다.
    with open(dbc_file, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            # BO_ <ID> <Name>: <DLC> <Node>
            match = re.match(r'BO_\s+(\d+)\s+(\w+):\s+\d+\s+\w+', line)
            if match:
                message_id = int(match.group(1))
                message_name = match.group(2)
                message_ids[message_name] = message_id
    return message_ids

def export_to_csv(messages, message_ids, output_file):
    """
    메시지와 신호를 CSV 파일로 내보냅니다.
    중복된 메시지도 모두 출력합니다.
    """
    with open(output_file, mode='w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Message Name", "Message ID", "Signal Name", "Start Bit", "Length", "Unit"])

        for message in messages:
            message_id = getattr(message, 'frame_id', None) or getattr(message, 'id', None)
            if message_id is None:
                message_id = message_ids.get(message.name, "N/A")
            
            if isinstance(message_id, int):
                message_id = hex(message_id)

            for signal in message.signals:
                csv_writer.writerow([
                    message.name,
                    message_id,
                    signal.name,
                    signal.start_bit,
                    signal.size,
                    signal.unit
                ])
    print(f"CSV 파일로 변환 완료: {output_file}")

def main(input_file, output_file):
    """
    DBC 파일을 읽고 중복된 메시지도 포함하여 CSV로 출력합니다.
    """
    print(f"Loading DBC file: {input_file}")
    
    # DBC 파일에서 메시지 ID를 직접 추출
    message_ids = extract_ids_from_dbc(input_file)
    
    # canmatrix를 사용하여 DBC 파일 읽기
    db = canmatrix.formats.loadp(input_file)

    all_messages = []
    for db_matrix in db.values():
        all_messages.extend(db_matrix.frames)

    export_to_csv(all_messages, message_ids, output_file)

if __name__ == "__main__":
    input_dbc = "OK1 + VSTD CAN Protocol-2024.08.29.dbc"
    output_csv = "output.csv"
    main(input_dbc, output_csv)

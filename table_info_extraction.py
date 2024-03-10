import json
from cross_page_table import find_table_end_page, merge_table
from multi_layer_table import header_boundary


def find_title_position(json_data, title):
    for page_id, item in json_data.items():
        table_list = item[0]['result']['tables']
        for table in table_list:
            if table['type'] == 'plain':
                for line in table['lines']:
                    if line['text'] == title:
                        return page_id, line['position'][-1]
    return None, None


def find_table_unit(page_item, title, title_position):
    table_found = False
    prev_line = ''
    table_list = page_item[0]['result']['tables']
    for table in table_list:
        if table['type'] == 'plain':
            for line in table['lines']:
                if line['position'][-1] > title_position:
                    prev_line = line['text']
        if table['type'] == 'table_with_line' and not table_found:
            if table['position'][-1] > title_position:
                table_found = True
                unit = '' if prev_line == title else prev_line
                return table, unit


# def extract_header(table):
#     return [cell['text'] for cell in table['table_cells'] if cell['start_row'] == 0]
def extract_header(table, header_end_row):
    cell_list = table['table_cells']
    max_col = max(cell['end_col'] for cell in cell_list)
    headers = [[''] * (max_col + 1) for _ in range(header_end_row + 1)]
    header_list = [cell for cell in cell_list if cell['end_row'] <= header_end_row]
    for header in header_list:
        for row in range(header['start_row'], header['end_row'] + 1):
            for col in range(header['start_col'], header['end_col'] + 1):
                headers[row][col] = header['text']
    return headers


def extract_key_index(table, header_end_row):
    return [cell['text'] for cell in table['table_cells'] if cell['start_col'] == 0 and cell['start_row'] > header_end_row]


def extract_values(table, header_end_row):
    values = []
    end_row = max(cell['end_row'] for cell in table['table_cells'])
    end_col = max(cell['end_col'] for cell in table['table_cells'])
    for row in range(header_end_row + 1, end_row + 1):
        temp = []
        for col in range(1, end_col + 1):
            for cell in table['table_cells']:
                if cell['start_row'] == row and cell['start_col'] == col:
                    temp.append(cell['text'])
        values.append(temp)
    return values


def extract_table_info(json_data, title):
    page_id, title_position = find_title_position(json_data, title)
    table, unit = find_table_unit(json_data[page_id], title, title_position)
    header_end_row = header_boundary(table)  # 确定表格头部的边界位置
    header = extract_header(table, header_end_row)
    for i in range(len(header)):
        for j in range(len(header[0])):
            header[i][j] = header[i][j].replace('\n', '')
    # header_modified = [item.replace('\n', '') for item in header]
    key_index = extract_key_index(table, header_end_row)
    key_index = [item.replace('\n', '') for item in key_index]
    values = extract_values(table, header_end_row)
    last_page_id = find_table_end_page(json_data, page_id, table)
    n = sorted(json_data.keys()).index(last_page_id) - sorted(json_data.keys()).index(page_id)
    # 判断是否有跨页情况
    if n > 0:
        key_index, values = merge_table(json_data, n, page_id, key_index, values)
    return {
        'title': title,
        'unit': unit,
        'header': header,
        'key_index': key_index,
        'values': values
    }


file_path = 'annual_report.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    title = input("Please enter the name of table you want to check: ")
    print(extract_table_info(data, title))




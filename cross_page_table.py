import json
import re


def find_table_end_page(json_data, start_page_id, current_table):
    pages = sorted(json_data.keys())
    current_index = pages.index(start_page_id)
    table = current_table
    end_page_id = start_page_id

    # 确保当前页面不是PDF的最后一页
    while current_index < len(pages) - 1:
        next_page_id = pages[current_index + 1]
        current_page_table_list = json_data[end_page_id][0]['result']['tables']
        for i in range(len(current_page_table_list)):
            if current_page_table_list[i] == table:
                current_page_next_table = current_page_table_list[i + 1]
                break

        # 判断该表格是否在本页的结尾处 + 下一页是否以表格开始
        if (current_page_next_table['type'] == 'plain' and re.match(r'\d+/203',
                                                                    current_page_next_table['lines'][0]['text'])) and (
                len(json_data[next_page_id][0]['result']['tables'][0]['lines']) == 1 and
                json_data[next_page_id][0]['result']['tables'][1][
                    'type'] == 'table_with_line'):
            end_page_id = next_page_id
            current_index += 1
            table = json_data[next_page_id][0]['result']['tables'][1]
        else:
            break

    return end_page_id


def merge_table(json_data, n, start_page_id, key_index, values):
    pages = sorted(json_data.keys())
    start_page_index = pages.index(start_page_id)
    key_index_modified = key_index
    values_modified = values
    # 从第二页开始对前面一页的内容进行补充
    for i in range(1, n + 1):
        current_page = pages[start_page_index + i]
        table = json_data[current_page][0]['result']['tables'][1]
        for cell in table['table_cells']:
            if cell['start_col'] == 0:
                extra_key_index = cell['text'].replace('\n', '')
                key_index_modified.append(extra_key_index)

        end_row = max(cell['start_row'] for cell in table['table_cells'])
        end_col = max(cell['start_col'] for cell in table['table_cells'])
        for row in range(end_row + 1):
            temp = []
            for col in range(1, end_col + 1):
                for cell in table['table_cells']:
                    if cell['start_row'] == row and cell['start_col'] == col:
                        temp.append(cell['text'])
            values_modified.append(temp)

    return key_index_modified, values_modified

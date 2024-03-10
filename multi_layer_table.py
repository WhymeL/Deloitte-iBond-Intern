def header_boundary(table):
    cells = table['table_cells']
    header_end_row = 0
    for cell in cells:
        if cell['start_row'] != cell['end_row'] and cell['end_row'] > header_end_row:
            header_end_row = cell['end_row']
    return header_end_row


def extract_headers_for_mlt(table, header_end_row):
    cell_list = table['table_cells']
    max_col = max(cell['end_col'] for cell in cell_list)
    headers = [[''] * (max_col + 1) for _ in range(header_end_row + 1)]
    header_list = [cell for cell in cell_list if cell['end_row'] <= header_end_row]
    for header in header_list:
        for row in range(header['start_row'], header['end_row'] + 1):
            for col in range(header['start_col'], header['end_col'] + 1):
                headers[row][col] = header['text']
    return headers

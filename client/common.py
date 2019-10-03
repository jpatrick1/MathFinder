def join(*parts):
    normalized_parts = []
    for p in parts:
        if p == "" or p is None:
            continue

        if p[0] == "/":
            p = p[1:]

        if p[-1] != "/":
            p = p + "/"

        normalized_parts.append(p)

    url = ''.join(normalized_parts)
    url = url if url[-1] != "/" else url[:-1]
    return url

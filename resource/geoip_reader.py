from struct import pack, unpack

def ip2int(ip_str):
    b = map(lambda x: int(x), ip_str.split('.'))
    b = list(b)
    buf = pack('!BBBB', b[0], b[1], b[2], b[3])
    o = unpack('!I', buf)[0]
    return o

def load_ipdb(file_path):
    ip_range_list = []
    with open(file_path) as f:
        for line in f:
            fields = line.strip().split(',')
            fields = [f[1:-1] for f in fields]
            if len(fields) != 5:
                stderr.write(line)
                continue
            ip_start, ip_end, nation, province, city = fields
            ip_start = ip2int(ip_start)
            ip_end = ip2int(ip_end)
            ip_range_list.append((ip_start, ip_end, province, city))

    return ip_range_list

def ip_lookup(ip_range_list, ip):
    ip_bin = ip2int(ip)
    min_idx = 0
    max_idx = len(ip_range_list)
    mid = 0
    while True:
        if min_idx > max_idx:
            break
        mid = (min_idx + max_idx) / 2
        entry = ip_range_list[mid]
        if ip_bin > entry[1]:
            min_idx = mid + 1
            continue
        elif ip_bin < entry[0]:
            max_idx = mid - 1
            continue
        else:
            break
    if ip_bin >= entry[0] and ip_bin <= entry[1]:
        return entry[2]
    else:
        return None
import re


def subnet_calc():
    try:

        while True:
            # IP주소를 입력받아 저장.
            input_ip = input("\nIP주소를 입력해주세요: ")

            # 입력받은 IP주소의 유효성을 체크합니다.
            octet_ip = input_ip.split(".")
            int_octet_ip = [int(i) for i in octet_ip]

            if (len(int_octet_ip) == 4) and \
                    (int_octet_ip[0] != 127) and \
                    (int_octet_ip[0] != 169) and  \
                    (0 <= int_octet_ip[1] <= 255) and \
                    (0 <= int_octet_ip[2] <=255) and \
                    (0 <= int_octet_ip[3] <= 255):
                break
            else:
                print("잘못된 IP주소 입니다.\n")
                continue

        # 사용 가능한 서브넷마스크 주소
        masks = [0, 128, 192, 224, 240, 248, 252, 254, 255]
        while True:

            # 서브넷 마스크 주소 입력요청
            input_subnet = input("\n서브넷 마스크 주소를 입력하세요: ")

            # 서브넷 마스크와 넷마스크비트를 모두 받을수있도록 함.
            p = re.compile('^/')
            m = p.match(input_subnet)

            if m:
                input_subnet = int(input_subnet.split('/')[1])
                if 3 < input_subnet < 33:
                    cidr = int(input_subnet)
                    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
                    input_subnet = (str((0xff000000 & mask) >> 24) + '.' +
                            str((0x00ff0000 & mask) >> 16) + '.' +
                            str((0x0000ff00 & mask) >> 8) + '.' +
                            str((0x000000ff & mask)))
                else:
                    print("잘못된 서브넷 마스크 주소 입니다.\n")
                    continue
            octet_subnet = [int(j) for j in input_subnet.split(".")]
            if (len(octet_subnet) == 4) and \
                    (octet_subnet[0] == 255) and \
                    (octet_subnet[1] in masks) and \
                    (octet_subnet[2] in masks) and \
                    (octet_subnet[3] in masks) and \
                    (octet_subnet[0] >= octet_subnet[1] >= octet_subnet[2] >= octet_subnet[3]):
                break
            else:
                print("잘못된 서브넷 마스크 주소 입니다.\n")
                continue

        # IP와 subnet를 바이너리로 바꿉니다.
        ip_in_binary = []

        # 각각의 IP주소 옥텟을 바이너리로 변경.
        # 예: 192.168.2.1 => ['11000000', '10101000', '10', '1']
        ip_in_bin_octets = [bin(i).split("b")[1] for i in int_octet_ip]

        # make each binary octet of 8 bit length by padding zeros
        # 각 옥텟의 8비트 길이 만큼 각각 0으로 채움.
        # 예: 192.168.2.1 => ['11000000', '10101000', '10', '1'] => ['11000000', '10101000', '00000010', '00000001']
        for i in range(0,len(ip_in_bin_octets)):
            if len(ip_in_bin_octets[i]) < 8:
                padded_bin = ip_in_bin_octets[i].zfill(8)
                ip_in_binary.append(padded_bin)
            else:
                ip_in_binary.append(ip_in_bin_octets[i])

        # 각가의 옥텟을 모두 결합시킵니다.
        #
        ip_bin_mask = "".join(ip_in_binary)

        sub_in_bin = []

        # 각가의 서브넷옥텟을 바이너리로 변경
        sub_bin_octet = [bin(i).split("b")[1] for i in octet_subnet]

        # make each binary octet of 8 bit length by padding zeros
        # 모두 0으로 채웁니다.
        for i in sub_bin_octet:
            if len(i) < 8:
                sub_padded = i.zfill(8)
                sub_in_bin.append(sub_padded)
            else:
                sub_in_bin.append(i)

        sub_bin_mask = "".join(sub_in_bin)

        # 호스트의 개수를 개산합니다.
        no_zeros = sub_bin_mask.count("0")
        no_ones = 32 - no_zeros
        no_hosts = abs(2 ** no_zeros - 2)

        # 와일드 마스크 개수를 개산합니다.
        wild_mask = []
        for i in octet_subnet:
            wild_bit = 255 - i
            wild_mask.append(wild_bit)

        wildcard = ".".join([str(i) for i in wild_mask])

        # 네트워크와 브로드캐스트 주소를 계산합니다.
        network_add_bin = ip_bin_mask[:no_ones] + "0" * no_zeros
        broadcast_add_bin = ip_bin_mask[:no_ones] + "1" * no_zeros

        network_add_bin_octet = []
        broadcast_binoct = []

        [network_add_bin_octet.append(i) for i in [network_add_bin[j:j+8]
                                                   for j in range(0, len(network_add_bin), 8)]]
        [broadcast_binoct.append(i) for i in [broadcast_add_bin[j:j+8]
                                              for j in range(0,len(broadcast_add_bin),8)]]

        network_add_dec_final = ".".join([str(int(i,2)) for i in network_add_bin_octet])
        broadcast_add_dec_final = ".".join([str(int(i,2)) for i in broadcast_binoct])

        # IP주소(호스트주소)의 범위를 계산합니다.
        first_ip_host = network_add_bin_octet[0:3] + [(bin(int(network_add_bin_octet[3],2)+1).split("b")[1].zfill(8))]
        first_ip = ".".join([str(int(i,2)) for i in first_ip_host])

        last_ip_host = broadcast_binoct[0:3] + [bin(int(broadcast_binoct[3],2) - 1).split("b")[1].zfill(8)]
        last_ip = ".".join([str(int(i,2)) for i in last_ip_host])

        # 결과 도출
        print("\n입력한 IP주소: " + input_ip)
        print("입력한 서브넷주소: " + input_subnet)
        print("===================================")
        print("서브넷 호스트 개수: {0}".format(str(no_hosts)))
        print("마스크 비트(mask bits): {0}".format(str(no_ones)))
        print("와일드 마스크(wildcard mask): {0}".format(wildcard))
        print("네트워크 주소: {0}".format(network_add_dec_final))
        print("브로드케스트 네트워크 주소: {0}".format(broadcast_add_dec_final))
        print("IP주소 범위: {0} - {1}".format(first_ip, last_ip))
        print("최대 서브넷 주소: " + str(2**abs(24 - no_ones)))

    except KeyboardInterrupt:
        print("Interrupted by the User, exiting\n")
    except ValueError:
        print("Seem to have entered an incorrect value, exiting\n")


if __name__ == '__main__':
    subnet_calc()
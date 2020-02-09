
import re


def subnet_calc():
    try:

        while True:
            # Take IP as input
            input_ip = input("\nIP주소를 입력해주세요: ")

            # Validate the IP
            octet_ip = input_ip.split(".")
            #print octet_ip
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

        # Predefine possible subnet masks
        masks = [0, 128, 192, 224, 240, 248, 252, 254, 255]
        while True:

            # Take subnet mask as input
            input_subnet = input("\n서브넷 마스크 주소를 입력하세요: ")

            # Validate the subnet mask

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
            # print octet_subnet
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

# Converting IP and subnet to binary

        ip_in_binary = []

        # Convert each IP octet to binary
        ip_in_bin_octets = [bin(i).split("b")[1] for i in int_octet_ip]

        # make each binary octet of 8 bit length by padding zeros
        for i in range(0,len(ip_in_bin_octets)):
            if len(ip_in_bin_octets[i]) < 8:
                padded_bin = ip_in_bin_octets[i].zfill(8)
                ip_in_binary.append(padded_bin)
            else:
                ip_in_binary.append(ip_in_bin_octets[i])

        # join the binary octets
        ip_bin_mask = "".join(ip_in_binary)

        # print ip_bin_mask

        sub_in_bin = []

        # convert each subnet octet to binary
        sub_bin_octet = [bin(i).split("b")[1] for i in octet_subnet]

        # make each binary octet of 8 bit length by padding zeros
        for i in sub_bin_octet:
            if len(i) < 8:
                sub_padded = i.zfill(8)
                sub_in_bin.append(sub_padded)
            else:
                sub_in_bin.append(i)

        # print sub_in_bin
        sub_bin_mask = "".join(sub_in_bin)

        # calculating number of hosts
        no_zeros = sub_bin_mask.count("0")
        no_ones = 32 - no_zeros
        no_hosts = abs(2 ** no_zeros - 2)

        # Calculating wildcard mask
        wild_mask = []
        for i in octet_subnet:
            wild_bit = 255 - i
            wild_mask.append(wild_bit)

        wildcard = ".".join([str(i) for i in wild_mask])

        # Calculating the network and broadcast address
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

        # Calculate the host IP range
        first_ip_host = network_add_bin_octet[0:3] + [(bin(int(network_add_bin_octet[3],2)+1).split("b")[1].zfill(8))]
        first_ip = ".".join([str(int(i,2)) for i in first_ip_host])

        last_ip_host = broadcast_binoct[0:3] + [bin(int(broadcast_binoct[3],2) - 1).split("b")[1].zfill(8)]
        last_ip = ".".join([str(int(i,2)) for i in last_ip_host])

        # print all the computed results
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


# Calling the above defined function
if __name__ == '__main__':
    subnet_calc()
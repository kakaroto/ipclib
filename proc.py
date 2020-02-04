proc_addresses = {
    "RESET_ME_CALL": {
        "CSE_C0_T0": 0x3FFBE
    },
    "BUP_ENTRY": {
        "SPT_CSME_C0_T0": 0x2D000,
        "KBP_CSME_C0_T0": 0x31000,
        "CSE_C0_T0": 0x26000
    },
    "SYSLIB:MALLOC": {
        "CSE_C0_T0": 0x6078
    },
    "SYSLIB:MALIGN": {
        "CSE_C0_T0": 0x6087
    },
    "XHCI_PORTID": {
        "SPT_CSME_C0_T0": 0xe6,
        "KBP_CSME_C0_T0": 0xe6,
        "CSE_C0_T0": 0xa2
    },
    "XHCI_PCI_DEVICE": {
        "SPT_CSME_C0_T0": 20,
        "KBP_CSME_C0_T0": 20,
        "CSE_C0_T0": 21
    },        
    "SB_CHANNEL": {
        "SPT_CSME_C0_T0": 0xF00A90E0,
        "KBP_CSME_C0_T0": 0xF00A9000,
        "CSE_C0_T0": 0xF00A9000
    },
    "SB_WINDOW_MMIO": {
        "SPT_CSME_C0_T0": 0xF5048000,
        "KBP_CSME_C0_T0": 0xF5020000,
        "CSE_C0_T0": 0xF6110000
    },
    "MMIOS": {
        "SPT_CSME_C0_T0": [
            (0xF5022000, 0x00000C00),
            (0xF5029000, 0x00001000),
            (0xF461A000, 0x00002000),
            (0xF4628000, 0x00004000),
            (0xF00B9000, 0x00001000),
            (0xF0080000, 0x00006000),
            (0xF0088000, 0x00006000),
            (0xF00D8000, 0x00006000),
            (0xF5018000, 0x00002000),
            (0xF5108000, 0x00001000),
            (0xF510B000, 0x00001000),
            (0xF510C000, 0x00001000),
            (0xF510D000, 0x00001000),
            (0xF510E000, 0x00001000),
            (0xF510F000, 0x00000484),
            (0xF5038000, 0x00001000),
            (0xF0098000, 0x00006000),
            (0xF00A8000, 0x00001000),
            (0xF00A9000, 0x00001000),
            (0xF00AA000, 0x00001000),
            (0xF00AB000, 0x00001000),
            (0xF00AC000, 0x00001000),
            (0xF7000000, 0x00020000),
            (0xF7400000, 0x00100000),
            (0xF00A8000, 0x00005000),
            (0xF00A0000, 0x00006000),
            (0xF5050000, 0x00010000),
            (0xF0090000, 0x00006000),
            (0xF461E000, 0x00001000),
            (0xF3000000, 0x01000000),
            (0xF0099000, 0x00001000),
            (0xF00B1050, 0x00000004),
            (0xF00B1004, 0x00000004),
            (0xF5010000, 0x00001000),
            (0xE00C0000, 0x00001000),
            (0xF4630000, 0x00010000),
            (0xF4623000, 0x00001000),
            (0xF5048000, 0x00008000),
            (0xF1000000, 0x00001000),
            (0xF1007000, 0x00001000),
            (0xE00D0000, 0x00001000),
            (0xE0052000, 0x00001000),
            (0xF4622000, 0x00001000)
        ],
        "KBP_CSME_C0_T0": [
            (0xF5022000, 0x00000C00),
            (0xF5029000, 0x00001000),
            (0xF461A000, 0x00002000),
            (0xF4628000, 0x00004000),
            (0xF00B9000, 0x00001000),
            (0xF00B9000, 0x00001000),
            (0xF00B9000, 0x00001000),
            (0xF00B9000, 0x00001000),
            (0xF00B9000, 0x00001000),
            (0xF00B9000, 0x00001000),
            (0xF0080000, 0x00006000),
            (0xF0088000, 0x00006000),
            (0xF00D8000, 0x00006000),
            (0xF5018000, 0x00004000),
            (0xF501C000, 0x00004000),
            (0xF5016000, 0x00002000),
            (0xF5108000, 0x00001000),
            (0xF510B000, 0x00001000),
            (0xF510C000, 0x00001000),
            (0xF510D000, 0x00001000),
            (0xF510E000, 0x00001000),
            (0xF510F000, 0x00000484),
            (0xF5038000, 0x00001000),
            (0xF0098000, 0x00006000),
            (0xF7000000, 0x00020000),
            (0xF7400000, 0x00100000),
            (0xF00A0000, 0x00006000),
            (0xF5050000, 0x00010000),
            (0xF5060000, 0x00010000),
            (0xF5070000, 0x00010000),
            (0xF5080000, 0x00010000),
            (0xF5090000, 0x00010000),
            (0xF50A0000, 0x00010000),
            (0xF50B0000, 0x00010000),
            (0xF50C0000, 0x00010000),
            (0xF50D0000, 0x00010000),
            (0xF50F0000, 0x00010000),
            (0xF50E0000, 0x00010000),
            (0xF4790000, 0x00010000),
            (0xF47A0000, 0x00010000),
            (0xF4768000, 0x00008000),
            (0xF4770000, 0x00008000),
            (0xF4758000, 0x00004000),
            (0xF475C000, 0x00004000),
            (0xF4767000, 0x00001000),
            (0xF4783000, 0x00001000),
            (0xF0090000, 0x00006000),
            (0xF461E000, 0x00001000),
            (0xF3000000, 0x01000000),
            (0xF0099000, 0x00001000),
            (0xF00B1050, 0x00000004),
            (0xF00B1004, 0x00000004),
            (0xF5010000, 0x00001000),
            (0xF5011000, 0x00001000),
            (0xF5012000, 0x00002000),
            (0xE00C0000, 0x00001000),
            (0xF4630000, 0x00010000),
            (0xF4623000, 0x00001000),
            (0xF5048000, 0x00008000),
            (0xF1000000, 0x00001000),
            (0xF1007000, 0x00001000),
            (0xE00D0000, 0x00001000),
            (0xE0052000, 0x00001000),
            (0xF4622000, 0x00001000),
            (0xF5200000, 0x00010000)  
        ],
        "CSE_C0_T0": [
            # MMIO Ranges from bup metadata
            (0xF4000000, 0x00026000),
            (0xF00B4000, 0x00000200),
            (0xF5029000, 0x00001000),
            (0xF461A000, 0x00002000),
            (0xFCEE0000, 0x00010000),
            (0xF4624000, 0x00002000),
            (0xF6D00000, 0x00010000),
            (0xF0080000, 0x00006000),
            (0xF0088000, 0x00006000),
            (0xF00D8000, 0x00006000),
            (0xF5018000, 0x00002000),
            (0xF5108000, 0x00001000),
            (0xF510B000, 0x00001000),
            (0xF510C000, 0x00001000),
            (0xF510D000, 0x00001000),
            (0xF510E000, 0x00001000),
            (0xF510F000, 0x00000484),
            (0xF5038000, 0x00001000),
            (0xF00A8000, 0x00001000),
            (0xF00A9000, 0x00001000),
            (0xF00AA000, 0x00001000),
            (0xF00AB000, 0x00001000),
            (0xF00AC000, 0x00001000),
            (0xF4400000, 0x000B0000),
            (0xF00A8000, 0x00005000),
            (0xF00A0000, 0x00006000),
            (0xF0090000, 0x00006000),
            (0xFEDFD000, 0x00001000),
            (0xF3000000, 0x01000000),
            (0xF00D0000, 0x00006000),
            (0xDF800000, 0x00800000),
            (0xF60D0000, 0x00010000),
            (0xF0099000, 0x00001000),
            (0xF6050000, 0x00010000),
            (0xFEDFE000, 0x00001000),
            (0xFEDFF000, 0x00001000),
            (0xF00B1050, 0x00000004),
            (0xF00B1004, 0x00000004),
            (0xF5010000, 0x00001000),
            (0xE00C0000, 0x00001000),
            (0xF4630000, 0x00010000),
            (0xF4623000, 0x00001000),
            (0xF1000000, 0x00001000),
            (0xF1010000, 0x00001000),
            (0xE0070000, 0x00001000),
            (0xE00D0000, 0x00001000),
            (0xC8000000, 0x02000000),
            (0xF00B0000, 0x00001000),
            (0xF00B1000, 0x00000004),
            (0x10000000, 0x20000000),
            (0x10000000, 0x10000000),
            (0xF6110000, 0x00010000),
            (0xF5048000, 0x00008000),
            (0xF6030000, 0x00010000),
            # Potential PCI ?
            (0xE0000000, 0x1000),
            (0xE0010000, 0x1000),
            (0xE0020000, 0x1000),
            (0xE0030000, 0x1000),
            (0xE0040000, 0x1000),
            (0xE0050000, 0x1000),
            (0xE0060000, 0x1000),
            (0xE0070000, 0x1000),
            (0xE0080000, 0x1000),
            (0xE0090000, 0x1000),
            (0xE00a0000, 0x1000),
            (0xE00b0000, 0x1000),
            (0xE00c0000, 0x1000),
            (0xE00d0000, 0x1000),
            (0xE00e0000, 0x1000),
            (0xE00f0000, 0x1000),
            # Ranges from F00A8000 file
            (0xF6110000, 0x10000),
            (0xF1FF0000, 0xC000),
            (0xF5018000, 0x2000),
            (0xF5028000, 0x2000),
            (0xF5038000, 0x1000),
            (0xF5048000, 0x8000),
            (0xF6D00000, 0x10000),
            # Ranges from F6110000 file, sizes assumed
            (0xFF06C000, 0x1000),
            (0xFE042000, 0x2000),
            (0xFE044000, 0x2000),
            (0xFE900000, 0x2000),
            (0xFE902000, 0x2000),
            (0xFF006000, 0x1000),
            (0xFF007000, 0x1000),
            (0xFEA10000, 0x10000),
            (0xFE970000, 0x8000),
            (0xFE978000, 0x8000),
            (0xD370A000, 0x1000),
            (0xD3709000, 0x1000),
            (0xD3708000, 0x1000),
            (0xFCEE0000, 0x1000),
            (0x10000000, 0x1000),
            (0xFED01000, 0x1000),
            (0xFEDFD000, 0x1000),
            (0xFE000000, 0x1000),
            (0xF2000000, 0x1000),
            (0xFF000000, 0x1000),
            (0xD0000000, 0x10000),
            # Ranges from busdrv module
            (0xF4000000, 0x00026000),
            (0xF5028000, 0x00001000),
            (0xF5028000, 0x00001000),
            (0xF5028000, 0x00001000),
            (0xF5028000, 0x00008000),
            (0xF00A8000, 0x00005000),
            (0xF00B0000, 0x00001000),
            (0xF5018000, 0x00002000),
            (0xF6D00000, 0x00010000),
            (0xF00B2000, 0x00000030),
            (0xF6030000, 0x00010000),
            (0xF1FE0000, 0x00010000),
            (0xF1000000, 0x00001000),
            (0xF1001000, 0x00001000),
            (0xF1002000, 0x00001000),
            (0xF1003000, 0x00001000),
            (0xF1010000, 0x00001000),
            (0xF1011000, 0x00001000),
            (0xF1012000, 0x00001000),
            (0xF1013000, 0x00001000),
            (0xF1014000, 0x00001000),
            (0xF1004000, 0x00001000),
            (0xF1005000, 0x00001000),
            (0xF1006000, 0x00001000),
            (0xF1008000, 0x00001000),
            (0xF1009000, 0x00001000),
            (0xF100A000, 0x00001000),
            (0xF100B000, 0x00001000),
            (0xE0040000, 0x00001000),
            (0xE0048000, 0x00001000),
            (0xE0049000, 0x00001000),
            (0xE0050000, 0x00001000),
            (0xE0051000, 0x00001000),
            (0xE0052000, 0x00001000),
            (0xE0053000, 0x00001000),
            (0xE0054000, 0x00001000),
            (0xE0055000, 0x00001000),
            (0xE0058000, 0x00001000),
            (0xE0060000, 0x00001000),
            (0xE0068000, 0x00001000),
            (0xE0069000, 0x00001000),
            (0xE006A000, 0x00001000),
            (0xE0070000, 0x00001000),
            (0xE00A9000, 0x00001000),
            (0xE00B0000, 0x00001000),
            (0xE00B1000, 0x00001000),
            (0xE00B2000, 0x00001000),
            (0xE00B3000, 0x00001000),
            (0xE00B8000, 0x00001000),
            (0xE00B9000, 0x00001000),
            (0xE00BA000, 0x00001000),
            (0xE00BB000, 0x00001000),
            (0xE00C8000, 0x00001000),
            (0xE00C9000, 0x00001000),
            (0xE00CA000, 0x00001000),
            (0xE00C0000, 0x00001000),
            (0xE00C1000, 0x00001000),
            (0xE00D0000, 0x00001000),
            (0xE00D8000, 0x00001000),
            (0xE00E0000, 0x00001000),
            (0xE00E8000, 0x00001000),
            (0xE0100000, 0x00001000),
            (0xE00C0000, 0x00001000),
            (0xF00B1030, 0x00000004),
            (0xF00B1034, 0x00000004),
            (0xF00B1038, 0x00000004),
            (0xF00B1004, 0x00000004),
            (0xF0080000, 0x0002D000),
            (0xFEDFE000, 0x00001000),
            (0xFEDFF000, 0x00001000),
            (0xDF800000, 0x00800000),
        ]
    }
}

def proc_get_address(thread, name, default=0):
    addr_table = proc_addresses.get(name, {})
    return addr_table.get(thread.name, default)

ALIGNMENT_HCENTER_VTOP_WRAP = {
            "horizontal": "center",
            "vertical": "top",
            "wrapText": True
}
ALIGNMENT_HCENTER_VCENTER = {
            "horizontal": "center",
            "vertical": "center"
}
BORDERS_BOTTOM_LEFT_RIGHT = {
            "bottom": {"style": "thin", "color": "000000"},
            "left": {"style": "thin", "color": "000000"},
            "right": {"style": "thin", "color": "000000"},
}
BORDERS_BOTTOM_LEFT_RIGHT_TOP = {
            "bottom": {"style": "thin", "color": "000000"},
            "left": {"style": "thin", "color": "000000"},
            "right": {"style": "thin", "color": "000000"},
            "top": {"style": "thin", "color": "000000"}
}
BORDERS_BOTTOM_LEFT_TOP = {
            "bottom": {"style": "thin", "color": "000000"},
            "left": {"style": "thin", "color": "000000"},
            "top": {"style": "thin", "color": "000000"}
}

BORDERS_BOTTOM_RIGHT_TOP = {
            "bottom": {"style": "thin", "color": "000000"},
            "right": {"style": "thin", "color": "000000"},
            "top": {"style": "thin", "color": "000000"}
}
BORDERS_BOTTOM_TOP = {
            "bottom": {"style": "thin", "color": "000000"},
            "top": {"style": "thin", "color": "000000"}
}
BORDERS_LEFT_RIGHT_TOP = {
            "left": {"style": "thin", "color": "000000"},
            "right": {"style": "thin", "color": "000000"},
            "top": {"style": "thin", "color": "000000"}
}
FONT_CALIBRI_BOLD_12 = {
    "fontName": "Calibri",
    "fontBold": True,
    "fontSize": 12
}
FONT_CALIBRI_NORMAL_12 = {
    "fontName": "Calibri",
    "fontBold": False,
    "fontSize": 12
}
FONT_CALIBRI_BOLD_14_YELLOW = {
    "fontName": "Calibri",
    "fontBold": True,
    "fontColor": "ffc000",
    "fontSize": 14
}
FONT_CALIBRI_BOLD_12_YELLOW = {
    "fontName": "Calibri",
    "fontBold": True,
    "fontColor": "ffc000",
    "fontSize": 12
}
FILLCOLOR_GREY = "d9d9d9"
FILLCOLOR_DARK_BLUE = "2e75b6"
FILLCOLOR_LIGHT_BLUE = "9dc3e6"
FILLCOLOR_GREEN = "c5e0b4"
NUMBER_FORMAT_CURRENCY = {
            "type": "currency",
            "symbol": "€",
            "decimalPlaces": 2
}


PARTNER_TABLE_FORMAT = [   
    # Partner information section,
    {
        "label": "Partner Number",
        "range": "B2:C2",
        "merge": True,
        "fillColor": FILLCOLOR_GREY,
        "alignment": "center"
    },
    {
        "label": "",
        "range": "D2:E2",
        "merge": True,
        "fillColor": "c5e0b4",
        "alignment": "center",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP
    },
    {
        "label": "Partner Acronym",
        "range": "B3:C3",
        "merge": True,
        "fillColor": "d9d9d9",
        "alignment": "center"
    },
    {
        "label": "",
        "range": "D3:E3",
        "merge": True,
        "fillColor": "c5e0b4",
        "alignment": "center",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP
    },
    {
        "label": "Partner ID Code",
        "range": "B4:C4",
        "merge": True,
        "fillColor": "d9d9d9",
        "alignment": "center"
    },
    {
        "label": "",
        "range": "D4:E4",
        "merge": True,
        "fillColor": "c5e0b4",
        "alignment": "center",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP
    },
    {
        "label": "Country",
        "range": "B5:C5",
        "merge": True,
        "fillColor": "d9d9d9",
        "alignment": "center"
    },
    {
        "label": "",
        "range": "D5:E5",
        "merge": True,
        "fillColor": "c5e0b4",
        "alignment": "center",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP
    },
    {
        "label": "Role",
        "range": "B6:C6",
        "merge": True,
        "fillColor": "d9d9d9",
        "alignment": "center"
    },
    {
        "label": "",
        "range": "D6:E6",
        "merge": True,
        "fillColor": "c5e0b4",
        "alignment": "center",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP
    },
 {
        "label": "Partner PM rate",
        "range": "B7:C7",
        "merge": True,
        "fillColor": "d9d9d9",
        "alignment": "center"
    },
    {
        "label": "",
        "range": "D7:E7",
        "merge": True,
        "fillColor": "c5e0b4",
        "alignment": "center",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fontName": "Calibri",
        "fontBold": True,
        "fontSize": 14
    },
    # TABLE 1
    {
        "label": "TABLE 1",
        "range": "B10",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "BUDGET",
        "range": "C10:X10",
        "merge": True,
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "0",
        "range": "B11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW

    },
    {
        "label": "1",
        "range": "C11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "2",
        "range": "D11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "3",
        "range": "E11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "4",
        "range": "F11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "5 (A)",
        "range": "G11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "6 (B)",
        "range": "H11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "7 (C1)",
        "range": "I11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "8 (C2)",
        "range": "J11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "9 (C3)",
        "range": "K11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "10 (D1)",
        "range": "L11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "11 (D2)",
        "range": "M11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "12 (E)",
        "range": "N11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "13",
        "range": "O11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "14",
        "range": "P11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "15",
        "range": "Q11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "16",
        "range": "R11",
       "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "17",
        "range": "S11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "18",
        "range": "T11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "19",
        "range": "U11",
       "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "20",
        "range": "W11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "21",
        "range": "X11",
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_12_YELLOW
    },
    {
        "label": "No.",
        "range": "B12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "PIC (Partner identification code)",
        "range": "C12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Name of beneficiary",
        "range": "D12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Country",
        "range": "E12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Role",
        "range": "F12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Personnel costs /€",
        "range": "G12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Sub\ncontracting\ncosts /€",
        "range": "H12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Purchase costs - Travel and substistence /€",
        "range": "I12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Purchase costs - Equipment /€",
        "range": "J12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Purchase costs - Other goods, works and services /€",
        "range": "K12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Financial support to third parties /€",
        "range": "L12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Internally invoiced goods and services /€"
               "(Unit costs- usual accounting practices)",
        "range": "M12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Indirect Costs /€",
        "range": "N12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Total eligible costs /€",
        "range": "O12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Funding rate",
        "range": "P12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Maximum EU contribution to eligible costs /€",
        "range": "Q12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Requested EU contribution to eligible costs /€",
        "range": "R12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Max grant amount",
        "range": "S12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Income generated by the action",
        "range": "T12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Financial contributions",
        "range": "U12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Own resources",
        "range": "W12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "Total estimated income",
        "range": "X12",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "",
        "range": "C13:X13",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY
        
    },
    {
        "label": "",
        "range": "G13:O13",
        "numberFormat": NUMBER_FORMAT_CURRENCY
        
    },
     {
        "label": "",
        "range": "Q13:Q13",
        "numberFormat": NUMBER_FORMAT_CURRENCY
        
    },
        {
        "label": "",
        "range": "B13",
        "formula": "=D2",
        "fillColor": "d9d9d9",
        "alignment": "center"
    },
    {
        "label": "",
        "range": "C13",
        "formula": "=D4"
    },
    {
        "label": "",
        "range": "D13",
        "formula": "=D3"
    },
    {
        "label": "",
        "range": "E13",
        "formula": "=D5"
    },
    {
        "label": "",
        "range": "F13",
        "formula": "=D6"
    },    
    {
        "label": "",
        "range": "G13",
        "formula": "=D7*B18"
    },
    {
        "label": "",
        "range": "H13",
        "formula": "=F24"
    },
    {
        "label": "",
        "range": "i13",
        "formula": "=F28"
    },
    {
        "label": "",
        "range": "j13",
        "formula": "=F29"
    },
    {
        "label": "",
        "range": "k13",
        "formula": "=F30"
    },
    {
        "label": "",
        "range": "l13",
        "formula": "=F35"
    },
    {
        "label": "",
        "range": "m13",
        "formula": "=F36"
    },
    {
        "label": "",
        "range": "n13",
        "formula": "=0.25*(SUM(G13:L13)-H13)"
    },
    {
        "label": "",
        "range": "o13",
        "formula": "=SUM(SUM(G13:N13)-L13)"
    },
    {
        "label": "",
        "range": "p13",
        "formula": "=G3"
    },
    {
        "label": "",
        "range": "q13",
        "formula": "=O13*P13"
    },
    {
        "label": "",
        "range": "r13",
        "formula": "=Q13"
    },
    {
        "label": "",
        "range": "s13",
        "formula": "=R13"
    },
    {
        "label": "",
        "range": "t13",
        "formula": ""
    },
    {
        "label": "",
        "range": "u13",
        "formula": ""
    },
    {
        "label": "",
        "range": "v13",
        "formula": ""
    },
    {
        "label": "",
        "range": "W13",
        "formula": ""
    },
    {
        "label": "",
        "range": "X13",
        "formula": "=S13+T13+U13+W13"
    },
    {
        "label": "",
        "range": "g14:X14",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_BOLD_12
        
    },
    {
        "label": "",
        "range": "G14:O14",
        "numberFormat": NUMBER_FORMAT_CURRENCY
        
    },
    {
        "label": "",
        "range": "Q14:Q14",
        "numberFormat": NUMBER_FORMAT_CURRENCY
        
    },
    {
        "label": "Total",
        "range": "C14",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "",
        "range": "D14:F14",
        "merge": True,
        "borders": BORDERS_BOTTOM_TOP
    },
    {
        "label": "",
        "range": "G14",
        "formula": "=SUM(G13:G13)"
    },
    {
        "label": "",
        "range": "H14",
        "formula": "=SUM(H13:H13)"
    },
    {
        "label": "",
        "range": "I14",
        "formula": "=I13"
    },
    {
        "label": "",
        "range": "J14",
        "formula": "=J13"
    },
    {
        "label": "",
        "range": "K14",
        "formula": "=K13"
    },
    {
        "label": "",
        "range": "L14",
        "formula": "=SUM(L13:L13)"
    },
    {
        "label": "",
        "range": "M14",
        "formula": "=SUM(M13:M13)"
    },
    {
        "label": "",
        "range": "N14",
        "formula": "=SUM(N13:N13)"
    },
    {
        "label": "",
        "range": "O14",
        "formula": "=SUM(G13:N13)"
    },
    {
        "label": "",
        "range": "P14",
        "formula": "=P13"
    },
    {
        "label": "",
        "range": "Q14",
        "formula": "=SUM(Q13:Q13)"
    },
    {
        "label": "",
        "range": "R14",
        "formula": "=SUM(R13:R13)"
    },
    {
        "label": "",
        "range": "S14",
        "formula": "=S13"
    },
    {
        "label": "",
        "range": "T14",
        "formula": "=T13"
    },
    {
        "label": "",
        "range": "U14",
        "formula": "=U13"
    },
    {
        "label": "",
        "range": "V14",
        "formula": "ausgeblendet"
    },
    {
        "label": "",
        "range": "W14",
        "formula": "=V13"
    },
    {
        "label": "",
        "range": "X14",
        "formula": "=X13"
    },
    # TABLE 2
    {
        "label": "TABLE 2",
        "range": "B16",
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "Number of Person-Months (PMs) across Work-Packages (WP)s",
        "range": "C16:Q16",
        "merge": True,
        "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "",
        "range": "B17:Q17",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Sum / WPs",
        "range": "B17",
    },
    {
        "label": "1",
        "range": "C17",
    },
    {
        "label": "2",
        "range": "D17",
    },
    {
        "label": "3",
        "range": "E17",
    },
    {
        "label": "4",
        "range": "F17",
    },
    {
        "label": "5",
        "range": "G17",
    },
    {
        "label": "6",
        "range": "H17",
    },
    {
        "label": "7",
        "range": "I17",
    },
    {
        "label": "8",
        "range": "J17",
    },
    {
        "label": "9",
        "range": "K17",
    },
    {
        "label": "10",
        "range": "L17",
    },
    {
        "label": "11",
        "range": "M17",
    },
    {
        "label": "12",
        "range": "N17",
    },
    {
        "label": "13",
        "range": "O17",
    },
    {
        "label": "14",
        "range": "P17",
    },
    {
        "label": "15",
        "range": "Q17",
    },
    {   "label":"",
        "range": "B18",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "formula": "=SUM(C18:Q18)"
    },
    {   "range": "C18:Q18",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN
    },
	#TABLE B
    {
        "label": "Table B",
        "range": "B20",
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "Subcontracting",
        "range": "C20:H20",
        "merge": True,
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "No. in T-1",
        "range": "B21",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Cost category B",
        "range": "C21",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
 {
        "label": "Subcontractor name ( if known)",
        "range": "D21:E21",
        "merge": True,
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Sum",
        "range": "F21",
 	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Explanation of function/role",
        "range": "G21:H21",
        "merge": True,
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
	{
        "label": "6",
        "range": "B22",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "6",
        "range": "B23",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },    
    {
        "label": "Subcontract 1",
        "range": "C22",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "D22:E22",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F22",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12,
        "numberFormat": NUMBER_FORMAT_CURRENCY
    },
    {
        "label": "",
        "range": "G22:H22",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },    
    {
        "label": "Subcontract 2",
        "range": "C23",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },        
    {
        "label": "",
        "range": "D23:E23",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F23",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12,
        "numberFormat": NUMBER_FORMAT_CURRENCY
    },
   {
        "label": "",
        "range": "G23:H23",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Total",
        "range": "C24",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font":FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Total",
        "range": "D24:E24",
        "borders": BORDERS_BOTTOM_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "",
        "range": "F24",
        "formula": "=SUM(F22:F23)",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_RIGHT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12,
        "numberFormat": NUMBER_FORMAT_CURRENCY
    },
	#TABLE C
    {
        "label": "Table C",
        "range": "B26",
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "Purchase costs",
        "range": "C26:H26",
        "merge": True,
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "No. in T-1",
        "range": "B27",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Cost category D",
        "range": "C27",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Name",
        "range": "D27:E27",
        "merge": True,
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Sum",
        "range": "F27",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Explanation of function/role",
        "range": "G27:H27",
        "merge": True,
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "7",
        "range": "B28",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "C1",
        "range": "C28",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Travel and substistence /€",
        "range": "D28:E28",
		"merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F28",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G28:H28",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "8",
        "range": "B29",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "C2",
        "range": "C29",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Equipment /€",
        "range": "D29:E29",
    	"merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F29",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G29:H29",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "9",
        "range": "B30",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "C3",
        "range": "C30",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Other goods, works and services /€",
        "range": "D30:E30",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F30",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G30:H30",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Total",
        "range": "C31",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
        {
        "label": "",
        "range": "D31:E31",
        "fillColor": FILLCOLOR_LIGHT_BLUE,
    },
    {
        "label": "",
        "range": "F31",
        "formula": "=SUM(F28:F30)",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12,
        "NumberFormat": NUMBER_FORMAT_CURRENCY
    },
    # TABLE D
    {
        "label": "Table D",
        "range": "B33",
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
	{
        "label": "Other cost categories",
        "range": "C33:H33",
        "merge": True,
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
	{
        "label": "No. in T-1",
        "range": "B34",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Cost category D",
        "range": "C34",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Name",
        "range": "D34:E34",
        "merge": True,
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Sum",
        "range": "F34",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "Explanation of function/role",
        "range": "G34:H34",
        "merge": True,
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "10",
        "range": "B35",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "11",
        "range": "B36",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "D1",
        "range": "C35",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
	{
        "label": "D2",
        "range": "C36",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Financial support to third parties /€",
        "range": "D35:E35",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F35",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G35:H35",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "fillColor": FILLCOLOR_GREEN
    },
	{
        "label": "Internally invoiced goods & services (Unit costs- usual"
        " accounting practices)  /€  ",
        "range": "D36:E36",
		"merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F36",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G36:H36",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN
    },
    {
        "label": "Total",
        "range": "C37",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
     {
        "label": "",
        "range": "D37:E37",
        "borders": BORDERS_BOTTOM_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "",
        "range": "F37",
        "formula": "=SUM(F35:F36)",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_RIGHT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12,
        "numberFormat": NUMBER_FORMAT_CURRENCY
    },
    # TABLE X
    {
        "label": "Table X",
        "range": "B40",
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
    {
        "label": "Other Explanations of Table 1",
        "range": "C40:H40",
        "merge": True,
    	"alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_DARK_BLUE,
        "font": FONT_CALIBRI_BOLD_14_YELLOW
    },
     {
        "label": "",
        "range": "B41:H41",
	    "alignment":ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "No. in T-1",
        "range": "B41",
    },
    {
        "label": "Cost category",
        "range": "C41",
    },
    {
        "label": "Costs category name",
        "range": "D41:E41",
        "merge": True,
    },
    {
        "label": "Sum",
        "range": "F41",
    },
    {
        "label": "Explanation",
        "range": "G41:H41",
        "merge": True,
    },
    {
        "label": "18",
        "range": "B42",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "C42",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY
    },
    {
        "label": "Income generated by the action",
        "range": "D42:E42",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
    },
    {
        "label": "",
        "range": "F42",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G42:H42",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN
    },
    {
        "label": "19",
        "range": "B43",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "C43",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY
    },
    {
        "label": "Financial contributions",
        "range": "D43:E43",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F43",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G43:H43",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN
    },
    {
        "label": "20",
        "range": "B44",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY
    },
    {
        "label": "",
        "range": "C44",
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY
    },
        {
        "label": "own resources",
        "range": "D44:E44",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREY,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "F44",
        "alignment": ALIGNMENT_HCENTER_VTOP_WRAP,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "numberFormat": NUMBER_FORMAT_CURRENCY,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "",
        "range": "G44:H44",
        "merge": True,
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_LEFT_RIGHT_TOP,
        "fillColor": FILLCOLOR_GREEN,
        "font": FONT_CALIBRI_NORMAL_12
    },
    {
        "label": "Total",
        "range": "C45",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders":BORDERS_BOTTOM_LEFT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12
    },
    {
        "label": "",
        "range": "D45:E45",
        "borders": BORDERS_BOTTOM_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE
    },
    {
        "label": "",
        "range": "F45",
        "formula": "=SUM(F42:F44)",
        "alignment": ALIGNMENT_HCENTER_VCENTER,
        "borders": BORDERS_BOTTOM_RIGHT_TOP,
        "fillColor": FILLCOLOR_LIGHT_BLUE,
        "font": FONT_CALIBRI_BOLD_12,
        "numberFormat": NUMBER_FORMAT_CURRENCY
    }
]
ROW_HEIGHTS = {
            1: 30.00,
            2: 30.00,
            3: 30.00,
            4: 30.00,
            5: 30.00,
            6: 30.00,
            7: 30.00,
            12: 128.88,
            16: 30.00,
            21: 30.00,
            22: 30.00,
            23: 30.00,
            24: 30.00,
            26: 30.00,
            27: 30.00,
            28: 30.00,
            29: 30.00,
            30: 30.00,
            31: 30.00,
            33: 30.00,
            34: 30.00,
            35: 30.00,
            36: 30.00,
            37: 30.00,
            40: 30.00,
            41: 30.00,
            42: 30.00,
            43: 30.00,
            44: 30.00,
            45: 30.00
        }
COLUMN_WIDTHS = {
            'C': 9,
            'D': 14
        }

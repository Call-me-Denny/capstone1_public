from fpdf import FPDF, XPos, YPos
import re

class MeetingPDF(FPDF):
    """ 
    Class for minutes of meeting pdf file 
    """
    def __init__(self):
        super().__init__()

        self.add_font("nanumbarungothic", fname="NanumBarunGothic.ttf")
        self.add_font("nanumbarungothic", style="B", fname="NanumBarunGothicBold.ttf")
        self.set_fill_color(r=225, g=255, b=225)
        self.b_margin = 25          # Bottom margin of a whole paper
        self.set_left_margin(25.0)  # Left margin of a whole paper
        self.set_right_margin(25.0) # Right margin of a whole paper
        self.head_w_left = 40.0     # Width of left cells int the head
        self.head_w_right = self.w - self.l_margin * 2 - self.head_w_left # Width of right cells in the head
        self.head_h = 15            # Height of the cells in the head
        self.head_font_size = 12    # Head font size
        self.content_font_size = 11 # Content font size
        self.cell_padding = 2.0     # Horizontal padding in each cell


    def footer(self):
        self.set_y(-1 * self.b_margin)
        self.set_font("Times", "", 11)
        self.cell(w=0, h=11, text=f"{self.page_no()}", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    

    def set_kor_font(self, size: float, style:str=""):
        """
        Set current font to Korean font 
        #### Params:
        * size: size of the font
        * style: `""` for regular font, `"B"` for bold face
        """
        self.set_font("nanumbarungothic", style=style, size=size)

    @property
    def accept_page_break(self):
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())

        return self.auto_page_break

def main():
    content_indent = 10.0

    outline_file_name = "06_02_test_outline.txt"
    opinion_file_name = "06_02_test_opinion.txt"
    decision_file_name = "06_02_test_decision.txt"

    # Opening and parsing the outline text file
    try: 
        with open(outline_file_name, "r", encoding="utf-8") as outline_file:
            lines = outline_file.readlines()
            for line in lines:
                if "date/time:" in line:
                    # found line which contains data & time 
                    date_time_str = line[line.index(": ") + 1:].strip()
                    date_str = date_time_str.split(" ")[0]
                    date_str = re.sub(r"(\d+)/(\d+)/(\d+)", r"\1년 \2월 \3일", date_str) # date_str = "YYYY년 MM월 DD일"
                    time_str = date_time_str.split(" ")[1]  # time_str = "HH:mm"
                elif "Participants:" in line:
                    # found line which contains participants
                    part_str = line.split(":")[1].strip()
    except FileNotFoundError:
        print("error: outline text file not found.")
        exit(1)

    # Opening and parsing the opinion text file
    try:
        with open(opinion_file_name, "r", encoding="utf-8") as opinion_file:
            lines = opinion_file.readlines()
            lines.pop(0) # Delete first line (It does not contain any useful info)
            agendas = {} # {'안건이름': ['의견 1', '의견 2', ...]}
            opinion_strs = {} # Dict of {'안건이름': '- Participant1: Opinion1\n- Participant2: Opinion2\n ...'}
            for line in lines:
                if line[0] == '-':
                    # Found a line which contains an agenda
                    agenda = line[1:].strip()
                    agendas[agenda] = []
                else:
                    # These lines contain opinions suggested for each agenda
                    agendas[agenda].append(line.strip())
            
            for k, v in agendas.items():
                opinion_strs[k] = ""
                for opinion in v:
                    opinion_strs[k] += opinion + "\n"
                opinion_strs[k] = opinion_strs[k][:-1] # Remove trailing '\n'
    except FileNotFoundError:
        print("error: opinion text file not found.")
        exit(1)
    
    # Open and parse the decision text file
    try :
        with open(decision_file_name, "r", encoding="utf-8") as decision_file:
            lines = decision_file.readlines()
            lines.pop(0) # Delete first line (It does not contain any useful info)
            decision_strs = {}
            for line in lines:
                if line[0] == '-':
                    # Found a line which contains an decision
                    agenda = line[1:].strip()
                    decision_strs[agenda] = ""
                else:
                    # These lines contain opinions suggested for each decision
                    decision_strs[agenda] += line.strip() + "\n"
            
            for k in decision_strs.keys():
                decision_strs[k] = decision_strs[k][:-1]
    except FileNotFoundError:
        print("error: decision text file not found.")
        exit(1)


    # Initializing pdf file
    pdf = MeetingPDF()

    # Add the first page
    pdf.add_page()

    # Title cell
    pdf.set_kor_font(18, "B")
    pdf.multi_cell(w=0, h=25, text="회  의  록", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    # print(pdf.t_margin) # for test
    pdf.set_top_margin(35.0)

    # Date cell
    pdf.set_kor_font(pdf.head_font_size, "B")
    pdf.multi_cell(w=pdf.head_w_left, h=pdf.head_h, text="일 시", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C", fill=True)
    pdf.set_kor_font(pdf.head_font_size)
    pdf.multi_cell(w=pdf.head_w_right, h=pdf.head_h, text=date_str, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", padding=(0.0, pdf.cell_padding))

    # Time cell
    pdf.set_kor_font(pdf.head_font_size, "B")
    pdf.multi_cell(w=pdf.head_w_left, h=pdf.head_h, text="회의시각", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C", fill=True)
    pdf.set_kor_font(pdf.head_font_size)
    pdf.multi_cell(w=pdf.head_w_right, h=pdf.head_h, text=time_str, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", padding=(0.0, pdf.cell_padding))

    # Participants cell
    pdf.set_kor_font(pdf.head_font_size, "B")
    pdf.multi_cell(w=pdf.head_w_left, h=pdf.head_h, text="참가자", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align="C", fill=True)
    pdf.set_kor_font(pdf.head_font_size)
    pdf.multi_cell(w=pdf.head_w_right, h=pdf.head_h, text= part_str, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", padding=(0.0, pdf.cell_padding))
    
    # Agendas cell
    pdf.set_kor_font(pdf.head_font_size, "B")
    pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=pdf.head_h, text="안 건", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    pdf.set_kor_font(pdf.content_font_size)
    for agenda in agendas.keys():
        pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=8, text=f"· {agenda}", border="LR", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", padding=(0.0, pdf.cell_padding))

    # Opinions cell
    pdf.set_kor_font(pdf.head_font_size, "B")
    pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=pdf.head_h, text="회의내용", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    for k, v in opinion_strs.items():
        pdf.set_kor_font(pdf.head_font_size, "B")
        pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=8, text=f"· {k}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, border="LR", align="L", max_line_height=8, padding=(0.0, pdf.cell_padding))
        pdf.set_kor_font(pdf.content_font_size)
        pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=8, text=v, border="LR", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", padding=(0.0, pdf.cell_padding, 0.0, content_indent))

    # Decisions cell
    pdf.set_kor_font(pdf.head_font_size, "B")
    pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=pdf.head_h, text="의결사항", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
    for k, v in decision_strs.items():
        pdf.set_kor_font(pdf.head_font_size, "B")
        pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=8, text=f"· {k}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, border="LR", align="L", max_line_height=8, padding=(0.0, pdf.cell_padding))
        pdf.set_kor_font(pdf.content_font_size)
        pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=8, text=v, border="LR", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L", padding=(0.0, pdf.cell_padding, 0.0, content_indent))

    # Dummy cell for bottom line 
    pdf.set_kor_font(0.1)
    pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=pdf.head_h, text=" ", border="T", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    # Draw missing lines at the top of each page
    page_no_temp = pdf.page_no()
    pdf.line(pdf.l_margin, pdf.t_margin, pdf.w - pdf.r_margin, pdf.t_margin)
    for i in range(pdf.page_no(), 1, -1):
        pdf.page = i
        pdf.line(pdf.l_margin, pdf.t_margin, pdf.w - pdf.r_margin, pdf.t_margin)
    pdf.page = page_no_temp

    # Generate the output pdf file
    pdf.output("summary.pdf")

if __name__ == "__main__":
    main()
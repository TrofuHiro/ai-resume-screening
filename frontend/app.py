import sys
import os
import requests
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QFileDialog,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QComboBox,
    QMessageBox
)
from PyQt6.QtGui import QColor

class ResumeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Resume Screening")
        self.resize(1280, 720)

        self.selected_file = None
        self.resume_skills = []
        self.resume_text = ""
        self.resume_id = None

        layout = QVBoxLayout()

        title = QLabel("AI Resume Screening System")
        layout.addWidget(title)

        self.graph_selector = QComboBox()
        self.graph_selector.addItems([
            "Skill Score",
            "Semantic Score",
            "Final Score"
        ])
        layout.addWidget(self.graph_selector)

        self.graph_btn = QPushButton("Show Graph")
        self.graph_btn.clicked.connect(self.show_graph)
        layout.addWidget(self.graph_btn)

        self.upload_btn = QPushButton("Upload Resume PDF")
        self.upload_btn.clicked.connect(self.upload_resume)
        layout.addWidget(self.upload_btn)

        self.job_input = QTextEdit()
        self.job_input.setPlaceholderText("Paste Job Description Here...")
        layout.addWidget(self.job_input)

        self.analyze_btn = QPushButton("Analyze Candidate")
        self.analyze_btn.clicked.connect(self.analyze_candidate)
        layout.addWidget(self.analyze_btn)

        self.history_btn = QPushButton("View History")
        self.history_btn.clicked.connect(self.load_history)
        layout.addWidget(self.history_btn)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["Resume ID", "Resume Name", "Score", "Recommendation", "Missing Skills"]
        )

        self.history_table.cellClicked.connect(self.show_candidate_detail)

        header = self.history_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch
        )

        self.history_table.verticalHeader().setVisible(False)
        self.history_table.verticalHeader().setDefaultSectionSize(40)

        self.history_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.history_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.history_table.setAlternatingRowColors(True)

        layout.addWidget(self.history_table)

        self.score_bar = QProgressBar()
        self.score_bar.setMinimum(0)
        self.score_bar.setMaximum(100)
        self.score_bar.setValue(0)
        layout.addWidget(self.score_bar)

        self.result_label = QLabel("Result will appear here")
        self.result_label.setStyleSheet("""
            background: white;
            border: 1px solid #d0d7e2;
            border-radius: 8px;
            padding: 12px;
        """)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)


        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fb;
                font-size: 13px;
                font-family: Segoe UI;
                color: black;
            }

            QPushButton {
                background-color: #4a6cf7;
                color: white;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #3654d6;
            }

            QTextEdit {
                background: white;
                color: black;
                border: 1px solid #d0d7e2;
                border-radius: 8px;
                padding: 6px;
            }

            QLabel {
                color: black;
            }

            QTableWidget {
                background: white;
                color: black;
                border: 1px solid #d0d7e2;
                gridline-color: #e5e5e5;
                selection-background-color: #dbe7ff;
                selection-color: black;
                alternate-background-color: #f8faff;
            }

            QHeaderView::section {
                background-color: #e9eefb;
                color: black;
                padding: 6px;
                border: none;
                font-weight: bold;
            }

            QProgressBar {
                color: black;
            }

                """)
        self.setLayout(layout)

    def upload_resume(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        self.selected_file = file_path
        filename = os.path.basename(file_path)

        self.result_label.setText("Uploading resume...")

        try:
            with open(file_path, "rb") as pdf_file:
                files = {
                    "file": (filename, pdf_file, "application/pdf")
                }

                response = requests.post(
                    "http://127.0.0.1:8000/upload-resume",
                    files=files
                )

            if response.status_code == 200:
                data = response.json()


                self.resume_skills = data.get("skills", [])
                self.resume_text = data.get("resume_text", "")
                self.resume_id = data.get("resume_id", None)

                skill_text = ", ".join(self.resume_skills)

                self.result_label.setText(
                    f"Uploaded: {filename}\n"
                    f"Resume ID: {self.resume_id}\n"
                    f"Skills: {skill_text}"
                )
            else:
                self.result_label.setText(
                    f"Upload Failed: {response.status_code}\n{response.text}"
                )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")

    def update_score_color(self, score):
        if score >= 80:
            color = "#4CAF50"
        elif score >= 50:
            color = "#FFC107"
        else:
            color = "#F44336"

        self.score_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)

    def analyze_candidate(self):
        if not self.resume_skills:
            self.result_label.setText("Please upload resume first")
            return

        job_description = self.job_input.toPlainText()

        if not job_description.strip():
            self.result_label.setText("Please enter job description")
            return

        payload = {
            "resume_skills": self.resume_skills,
            "resume_text": self.resume_text,
            "job_description": job_description,
            "resume_id": self.resume_id
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/match",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()

                score = data["score"]
                recommendation = data["recommendation"]
                skill_score = data["skill_score"]
                semantic_score = data["semantic_score"]

                matched = ", ".join(data["matched_skills"]) or "None"
                missing = ", ".join(data["missing_skills"]) or "None"

                score_int = round(score)

                self.score_bar.setValue(score_int)
                self.update_score_color(score_int)

                self.result_label.setText(
                    f"Final Score: {score}%\n"
                    f"Skill Score: {skill_score}%\n"
                    f"Semantic Score: {semantic_score}%\n\n"
                    f"Matched Skills: {matched}\n"
                    f"Missing Skills: {missing}\n\n"
                    f"Recommendation: {recommendation}"
                )
            else:
                self.result_label.setText(
                    f"Match Failed: {response.status_code}\n{response.text}"
                )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")
    
    def load_history(self):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/analysis-history"
            )

            if response.status_code != 200:
                self.result_label.setText("Failed to load history")
                return

            data = response.json()
            self.history_data = data

            self.history_table.setRowCount(len(data))

            for row_index, item in enumerate(data):
                self.history_table.setItem(
                    row_index, 0, self.make_item(item["resume_id"])
                )

                self.history_table.setItem(
                    row_index, 1, self.make_item(item["filename"])
                )

                self.history_table.setItem(
                    row_index, 2, self.make_item(item["score"])
                )

                self.history_table.setItem(
                    row_index, 3, self.make_item(item["recommendation"])
                )

                self.history_table.setItem(
                    row_index, 4, self.make_item(item["missing_skills"])
                )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")

    def make_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setForeground(QColor("black"))
        return item

    def show_graph(self):
        try:
            response = requests.get(
                "http://127.0.0.1:8000/analysis-history"
            )

            if response.status_code != 200:
                QMessageBox.warning(self, "Error", "Cannot load graph data")
                return

            data = response.json()

            if not data:
                QMessageBox.warning(self, "Error", "No history data found")
                return

            selected = self.graph_selector.currentText()

            x = []
            y = []

            for item in data:
                x.append(item["filename"])

                if selected == "Skill Score":
                    y.append(item["skill_score"])

                elif selected == "Semantic Score":
                    y.append(item["semantic_score"])

                else:
                    y.append(item["score"])

            plt.figure(figsize=(10, 5))
            plt.bar(x, y)
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("Score")
            plt.title(selected)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def show_candidate_detail(self, row, column):
        candidate = self.history_data[row]

        matched = candidate["matched_skills"]
        missing = candidate["missing_skills"]

        if matched:
            matched = "• " + matched.replace(",", "\n• ")
        else:
            matched = "None"

        if missing:
            missing = "• " + missing.replace(",", "\n• ")
        else:
            missing = "None"

        self.result_label.setText(
            f"Resume: {candidate['filename']}\n\n"
            f"Final Score: {candidate['score']}%\n"
            f"Skill Score: {candidate['skill_score']}%\n"
            f"Semantic Score: {candidate['semantic_score']}%\n\n"
            f"Matched Skills:\n{matched}\n\n"
            f"Missing Skills:\n{missing}\n\n"
            f"Recommendation: {candidate['recommendation']}"
        )

        score = round(candidate["score"])
        self.score_bar.setValue(score)
        self.update_score_color(score)


app = QApplication(sys.argv)
window = ResumeApp()
window.show()
sys.exit(app.exec())
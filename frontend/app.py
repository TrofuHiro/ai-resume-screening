import sys
import os
import requests

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
    QTableWidgetItem
)


class ResumeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Resume Screening")
        self.resize(700, 500)

        self.selected_file = None
        self.resume_skills = []
        self.resume_text = ""
        self.resume_id = None

        layout = QVBoxLayout()

        title = QLabel("AI Resume Screening System")
        layout.addWidget(title)

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

            self.history_table.setRowCount(len(data))

            for row_index, item in enumerate(data):
                self.history_table.setItem(
                    row_index,
                    0,
                    QTableWidgetItem(str(item["resume_id"]))
                )

                self.history_table.setItem(
                    row_index,
                    1,
                    QTableWidgetItem(item["filename"])
                )

                self.history_table.setItem(
                    row_index,
                    2,
                    QTableWidgetItem(str(item["score"]))
                )

                self.history_table.setItem(
                    row_index,
                    3,
                    QTableWidgetItem(item["recommendation"])
                )

                self.history_table.setItem(
                    row_index,
                    4,
                    QTableWidgetItem(item["missing_skills"])
                )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")


app = QApplication(sys.argv)
window = ResumeApp()
window.show()
sys.exit(app.exec())
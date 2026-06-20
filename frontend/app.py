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
    QProgressBar
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

        self.score_bar = QProgressBar()
        self.score_bar.setMinimum(0)
        self.score_bar.setMaximum(100)
        self.score_bar.setValue(0)
        layout.addWidget(self.score_bar)

        self.result_label = QLabel("Result will appear here")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)

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


app = QApplication(sys.argv)
window = ResumeApp()
window.show()
sys.exit(app.exec())
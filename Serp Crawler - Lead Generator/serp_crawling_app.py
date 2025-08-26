import sys
import pandas as pd
import asyncio
from functools import partial
import subprocess
import os
import codecs
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QListWidget, QTreeView, QListWidget, QAbstractItemView
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import aiohttp
from openai import OpenAI

base_path = os.path.dirname(__file__)
path = os.path.join(base_path, "Location Table.xlsx")
read_in_table = pd.read_excel(path, sheet_name='data_to_query', dtype=str)

api_token = 'blank'
api_url_pattern = 'https://serpstat.com/rt/api/v{version}?token={token}'
api_url = api_url_pattern.format(version=2, token=api_token)
headers = {"Content-Type": "application/json", "X-Api-Key": api_token}

class AsyncWorker(QThread):
    log_signal = pyqtSignal(str)
    task_id_signal = pyqtSignal(str)

    def __init__(self, serp_stat_id, city_name, keywords, parent=None):
        super().__init__(parent)
        self.serp_stat_id = serp_stat_id
        self.city_name = city_name
        self.keywords = keywords

    async def make_request(self, session, data):
        async with session.post(api_url, json=data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                if 'error' in result:
                    raise Exception(result['error'])
                return result
            else:
                raise Exception(await response.text())

    async def process_task(self):
        async with aiohttp.ClientSession() as session:
            data = {
                "id": "1",
                "method": "tasks.addKeywordList",
                "params": {
                    "keywords": self.keywords,
                    "typeId": 1,
                    "seId": 1,
                    "countryId": 23,
                    "langId": 1,
                    "regionId": str(self.serp_stat_id),
                }
            }
            results = await self.make_request(session, data)
            task_id = results['result']['task_id']
            self.task_id_signal.emit(task_id)
            self.log_signal.emit(f"Task ID for {self.city_name}: {task_id}")

            while True:
                data = {"id": "1", "method": "tasks.getList", "params": {}}
                results = await self.make_request(session, data)
                for item in results['result']:
                    if item['task_id'] != task_id:
                        continue
                    if item['parsed_at']:
                        self.log_signal.emit(f"Task for {self.city_name} is ready!")
                        return
                    else:
                        self.log_signal.emit(f"Task for {self.city_name} progress: {item['progress']}")
                await asyncio.sleep(2)

    def run(self):
        asyncio.run(self.process_task())

class SerpstatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.running_threads = []
        self.completed_task_ids = []
        self.task_industry_map = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Xoinx SERP Crawler")
        self.resize(1800, 1000)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.create_location_group())
        content_layout.addWidget(self.create_industry_group())
        content_layout.addWidget(self.create_actions_group())

        api_panel = self.create_api_panel()
        json_panel = self.getting_json_wiza_data()
        main_layout.addLayout(content_layout, stretch=3)

        main_layout.addWidget(api_panel)
        main_layout.addWidget(json_panel)

        self.setLayout(main_layout)
        self.update_states()

    def create_location_group(self):
        group = QGroupBox("Location Selection")
        layout = QGridLayout()
        layout.setSpacing(10)

        layout.addWidget(QLabel("Region Type:"), 0, 0)
        self.region_dropdown = QComboBox()
        self.region_dropdown.addItems(read_in_table["Region Type"].unique())
        self.region_dropdown.currentTextChanged.connect(self.update_states)
        layout.addWidget(self.region_dropdown, 0, 1)

        layout.addWidget(QLabel("State:"), 0, 2)
        self.state_dropdown = QComboBox()
        self.state_dropdown.currentTextChanged.connect(self.update_locations)
        layout.addWidget(self.state_dropdown, 0, 3)

        layout.addWidget(QLabel("Available Locations:"), 1, 0)
        self.location_list = QListWidget()
        self.location_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.location_list, 2, 0, 1, 2)

        layout.addWidget(QLabel("Picked Locations:"), 1, 3)
        self.picked_locations_list = QListWidget()
        self.picked_locations_list.itemDoubleClicked.connect(self.remove_selected_location)
        layout.addWidget(self.picked_locations_list, 2, 3)

        self.add_location_btn = QPushButton("Add >>")
        self.add_location_btn.clicked.connect(self.add_selected_locations)
        layout.addWidget(self.add_location_btn, 2, 2, Qt.AlignCenter)

        self.remove_location_btn = QPushButton("Remove Selected")
        self.remove_location_btn.clicked.connect(self.remove_selected_locations)
        layout.addWidget(self.remove_location_btn, 3, 3)

        group.setLayout(layout)
        return group

    def create_industry_group(self):
        group = QGroupBox("Industry & Keywords")
        layout = QHBoxLayout()
        layout.setSpacing(20)

        industry_layout = QVBoxLayout()
        industry_layout.addWidget(QLabel("Select Industry:"))
        self.industry_tree = QTreeView()
        self.industry_model = QStandardItemModel()
        self.industry_model.setHorizontalHeaderLabels(["Categories"])
        self.industry_tree.setModel(self.industry_model)
        self.populate_industry_tree()
        industry_layout.addWidget(self.industry_tree)
        layout.addLayout(industry_layout)

        keyword_layout = QVBoxLayout()
        keyword_layout.addWidget(QLabel("Keywords (one per line or comma-separated):"))
        self.keyword_input = QTextEdit()
        self.keyword_input.setPlaceholderText("e.g., keyword1, keyword2\nor\nkeyword1\nkeyword2")
        keyword_layout.addWidget(self.keyword_input)
        layout.addLayout(keyword_layout)

        group.setLayout(layout)
        return group

    def create_actions_group(self):
        group = QGroupBox("Actions & Logs")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        submit_layout = QHBoxLayout()
        self.submit_button = QPushButton("Submit Task")
        self.submit_button.clicked.connect(self.submit_task)
        submit_layout.addStretch()
        submit_layout.addWidget(self.submit_button)
        submit_layout.addStretch()
        layout.addLayout(submit_layout)

        layout.addWidget(QLabel("Logs:"))
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)

        group.setLayout(layout)
        return group

    def create_api_panel(self):
        panel = QGroupBox("AI Assistant for Keyword Generation or Information")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ChatGPT Section
        layout.addWidget(QLabel("ChatGPT API"))
        layout.addWidget(QLabel("Enter Query Below:"))
        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)
        layout.addWidget(QLabel("Response:"))
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.send_button = QPushButton("Send Request")
        self.send_button.clicked.connect(self.handle_request)
        button_layout.addWidget(self.send_button)

        layout.addLayout(button_layout)
        layout.addWidget(self.output_display)

        panel.setLayout(layout)
        return panel
    
    ## Working Here keep goping on it
    def getting_json_wiza_data(self):
        json_panel = QGroupBox("Wiza Information Required:")
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Dropdown for company location
        layout.addWidget(QLabel("Company Location:"))
        self.person_location_dropdown = QComboBox()
        us_states_with_country = [
            "Alabama, United States", "Alaska, United States", "Arizona, United States", "Arkansas, United States",
            "California, United States", "Colorado, United States", "Connecticut, United States", "Delaware, United States",
            "Florida, United States", "Georgia, United States", "Hawaii, United States", "Idaho, United States",
            "Illinois, United States", "Indiana, United States", "Iowa, United States", "Kansas, United States",
            "Kentucky, United States", "Louisiana, United States", "Maine, United States", "Maryland, United States",
            "Massachusetts, United States", "Michigan, United States", "Minnesota, United States", "Mississippi, United States",
            "Missouri, United States", "Montana, United States", "Nebraska, United States", "Nevada, United States",
            "New Hampshire, United States", "New Jersey, United States", "New Mexico, United States", "New York, United States",
            "North Carolina, United States", "North Dakota, United States", "Ohio, United States", "Oklahoma, United States",
            "Oregon, United States", "Pennsylvania, United States", "Rhode Island, United States", "South Carolina, United States",
            "South Dakota, United States", "Tennessee, United States", "Texas, United States", "Utah, United States",
            "Vermont, United States", "Virginia, United States", "Washington, United States", "West Virginia, United States",
            "Wisconsin, United States", "Wyoming, United States"
        ]
        self.person_location_dropdown.addItems(us_states_with_country)
        self.person_location_dropdown.addItem("None")
        layout.addWidget(self.person_location_dropdown)
        
        # Company Industry
        layout.addWidget(QLabel("Company Industry:"))
        self.company_industry_list = QComboBox()
        industries = ["accounting", "airlines/aviation", "alternative dispute resolution", "alternative medicine", "animation", "apparel & fashion", "architecture & planning", "arts and crafts", "automotive", "aviation & aerospace", "banking", "biotechnology", "broadcast media", "building materials", "business supplies and equipment", "capital markets", "chemicals", "civic & social organization", "civil engineering", "commercial real estate", "computer & network security", "computer games", "computer hardware", "computer networking", "computer software", "construction", "consumer electronics", "consumer goods", "consumer services", "cosmetics", "dairy", "defense & space", "design", "e-learning", "education management", "electrical/electronic manufacturing", "entertainment", "environmental services", "events services", "executive office", "facilities services", "farming", "financial services", "fine art", "fishery", "food & beverages", "food production", "fund-raising", "furniture", "gambling & casinos", "government administration", "government relations", "graphic design", "health, wellness and fitness", "higher education", "hospital & health care", "hospitality", "human resources", "import and export", "individual & family services", "industrial automation", "information services", "information technology and services", "insurance", "international affairs", "international trade and development", "internet", "investment banking", "investment management", "judiciary", "law enforcement", "law practice", "legal services", "legislative office", "libraries", "logistics and supply chain", "luxury goods & jewelry", "machinery", "management consulting", "maritime", "market research", "marketing and advertising", "mechanical or industrial engineering", "media production", "medical devices", "medical practice", "mental health care", "military", "mining & metals", "motion pictures and film", "museums and institutions", "music", "nanotechnology", "newspapers", "non-profit organization management", "oil & energy", "online media", "outsourcing/offshoring", "package/freight delivery", "packaging and containers", "paper & forest products", "performing arts", "pharmaceuticals", "philanthropy", "photography", "plastics", "political organization", "primary/secondary education", "printing", "professional training & coaching", "program development", "public policy", "public relations and communications", "public safety", "publishing", "railroad manufacture", "ranching", "real estate", "recreational facilities and services", "religious institutions", "renewables & environment", "research", "restaurants", "retail", "security and investigations", "semiconductors", "shipbuilding", "sporting goods", "sports", "staffing and recruiting", "supermarkets", "telecommunications", "textiles", "think tanks", "tobacco", "translation and localization", "transportation/trucking/railroad", "utilities", "venture capital & private equity", "veterinary", "warehousing", "wholesale", "wine and spirits", "wireless", "writing and editing"]
        self.company_industry_list.addItems(industries)
        layout.addWidget(self.company_industry_list)

        # Dropdown for company industry
        layout.addWidget(QLabel("Company Size:"))
        self.company_size_dropdown = QComboBox()
        self.company_size_dropdown.setEditable(True)  # Allows multi-selection
        self.company_size_dropdown.addItems(["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5001-10000", "10001+"])
        self.company_size_dropdown.addItem("None")
        layout.addWidget(self.company_size_dropdown)

        # Multi-select dropdown for revenue
        layout.addWidget(QLabel("Company Revenue:"))
        self.revenue_dropdown = QComboBox()
        self.revenue_dropdown.setEditable(True)  # Allows multi-selection
        self.revenue_dropdown.addItems(["$0-$1M", "$1M-$10M", "$10M-$25M", "$25M-$50M", "$50M-$100M", "$100M-$250M", "$250M-$500M", "$500M-$1B", "$1B-$10B", "$10B+"])
        self.revenue_dropdown.addItem("None")
        layout.addWidget(self.revenue_dropdown)

        layout.addWidget(QLabel("Job Title Level:"))
        self.job_title_level_list = QListWidget()
        self.job_title_level_list.addItems(["CXO", "Director", "Entry", "Manager", "Owner", "Partner", "Senior", "Training", "Unpaid", "VP"])
        self.job_title_level_list.setSelectionMode(QAbstractItemView.MultiSelection) 
        layout.addWidget(self.job_title_level_list)

        # Dropdown for Job Role
        layout.addWidget(QLabel("Job Role:"))
        self.job_role_dropdown = QListWidget()
        self.job_role_dropdown.setSelectionMode(QAbstractItemView.MultiSelection)
        job_roles = [
            "customer_service", "design", "education", "engineering", "finance", "health", 
            "human_resources", "legal", "marketing", "media", "operations", "public_relations", 
            "real_estate", "sales", "trades"
        ]
        self.job_role_dropdown.addItems(job_roles)
        layout.addWidget(self.job_role_dropdown)

        # Dropdown for Job Sub-Role
        layout.addWidget(QLabel("Job Sub-Role:"))
        self.job_sub_role_dropdown = QListWidget()
        self.job_sub_role_dropdown.setSelectionMode(QAbstractItemView.MultiSelection)
        job_sub_roles = [
            "accounting", "accounts", "brand_marketing", "broadcasting", "business_development", 
            "compensation", "content_marketing", "customer_success", "data", "dental", "devops", 
            "doctor", "editorial", "education_administration", "electrical", "employee_development", 
            "events", "fitness", "graphic_design", "information_technology", "instructor", "investment", 
            "journalism", "judicial", "lawyer", "logistics", "marketing_communications", "mechanical", 
            "media_relations", "network", "nursing", "office_management", "paralegal", "pipeline", 
            "product", "product_design", "product_marketing", "professor", "project_engineering", 
            "project_management", "property_management", "quality_assurance", "realtor", "recruiting", 
            "researcher", "security", "software", "support", "systems", "tax", "teacher", "therapy", 
            "video", "web", "web_design", "wellness", "writing"
        ]
        self.job_sub_role_dropdown.addItems(job_sub_roles)
        layout.addWidget(self.job_sub_role_dropdown)

        layout.addWidget(QLabel("Job Titles (one per line or comma-separated):"))
        self.job_title_input = QTextEdit()
        self.job_title_input.setPlaceholderText('e.g., "Account Manager", Engineer, Developer')
        layout.addWidget(self.job_title_input)

        json_panel.setLayout(layout)
        return json_panel


    def save_inputs_to_json(self):
        data = {
            "company_location": None if self.person_location_dropdown.currentText() == "None" else self.person_location_dropdown.currentText(),
            "company_industry": self.company_industry_list.currentText() or None,
            "company_size": None if self.company_size_dropdown.currentText() == "None" else self.company_size_dropdown.currentText(),
            "revenue": None if self.revenue_dropdown.currentText() == "None" else self.revenue_dropdown.currentText(),
            "job_title_level": [item.text() for item in self.job_title_level_list.selectedItems()] or None,
            "job_role": [item.text() for item in self.job_role_dropdown.selectedItems()] or None,  # Collect multi-selections
            "job_sub_role": [item.text() for item in self.job_sub_role_dropdown.selectedItems()] or None,  # Collect multi-selections
            "job_title": [title.strip() for title in self.job_title_input.toPlainText().split(",") if title.strip()] or None
        }

        with open(os.path.join(base_path, "wiza_inputs.json"), "w") as file:
            json.dump(data, file, indent=4)
        

    def handle_request(self):
        user_query = self.input_field.text()
        self.logs.append("Sending ChatGPT Request")
        response = self.call_chatgpt_api(user_query)
        self.output_display.setText(response)
        self.logs.append("ChatGPT Response Received")

    def call_chatgpt_api(self, query):
        client = OpenAI(api_key="blank")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{"role": "user", "content": query}]
        )
        return codecs.decode(completion.choices[0].message.content, 'unicode_escape')

    def populate_industry_tree(self):
        hierarchy_path = os.path.join(base_path, "Serpstat data _ Website Categories.xlsx")
        df = pd.read_excel(hierarchy_path, sheet_name="Website Categories")
        tree = {}
        for _, row in df.iterrows():
            levels = row['Cats'].split('/')
            current_level = tree
            for level in levels:
                if level not in current_level:
                    current_level[level] = {}
                current_level = current_level[level]

        def add_items(parent, items):
            for key, sub_items in items.items():
                item = QStandardItem(key)
                parent.appendRow(item)
                add_items(item, sub_items)

        add_items(self.industry_model.invisibleRootItem(), tree)
        self.industry_tree.selectionModel().selectionChanged.connect(self.on_industry_selected)

    def on_industry_selected(self, selected, deselected):
        selected_indexes = self.industry_tree.selectionModel().selectedIndexes()
        self.selected_industry = selected_indexes[0].data() if selected_indexes else "Unknown Industry"
        self.logs.append(f"Selected Industry: {self.selected_industry}")

    def remove_selected_location(self, item):
        self.picked_locations_list.takeItem(self.picked_locations_list.row(item))
        self.logs.append(f"Removed location: {item.text()}")

    def remove_selected_locations(self):
        for item in self.picked_locations_list.selectedItems():
            self.picked_locations_list.takeItem(self.picked_locations_list.row(item))
            self.logs.append(f"Removed location: {item.text()}")

    def update_states(self):
        region_type = self.region_dropdown.currentText()
        states = read_in_table[read_in_table["Region Type"] == region_type]["State Name"].unique()
        self.state_dropdown.clear()
        self.state_dropdown.addItems(states)
        self.update_locations()

    def update_locations(self):
        region_type = self.region_dropdown.currentText()
        state_name = self.state_dropdown.currentText()
        locations = read_in_table[
            (read_in_table["Region Type"] == region_type) & (read_in_table["State Name"] == state_name)
        ]["Location Name"]
        self.location_list.clear()
        self.location_list.addItems(locations)

    def add_selected_locations(self):
        for item in self.location_list.selectedItems():
            if not self.is_location_in_picked_list(item.text()):
                self.picked_locations_list.addItem(item.text())

    def is_location_in_picked_list(self, location_name):
        return any(self.picked_locations_list.item(i).text() == location_name 
                  for i in range(self.picked_locations_list.count()))

    def submit_task(self):
        self.save_inputs_to_json()
        self.logs.append("Wiza Inputs were Saved")
        picked_locations = [self.picked_locations_list.item(i).text() 
                          for i in range(self.picked_locations_list.count())]
        if not picked_locations:
            self.logs.append("Error: No locations selected.")
            return

        keyword_text = self.keyword_input.toPlainText()
        keywords = [kw.strip() for line in keyword_text.splitlines() 
                   for kw in line.split(",") if kw.strip()]
        if not keywords:
            self.logs.append("Error: No keywords provided.")
            return

        for location_name in picked_locations:
            try:
                serp_stat_id = read_in_table.loc[read_in_table["Location Name"] == location_name, "SerpStat ID"].iloc[0]
                self.logs.append(f"Submitting task for {location_name} (ID: {serp_stat_id})")
                worker = AsyncWorker(serp_stat_id, location_name, keywords)
                self.running_threads.append(worker)
                worker.log_signal.connect(self.logs.append)
                worker.finished.connect(partial(self.on_worker_finished, worker))
                worker.task_id_signal.connect(self.store_task_id)
                worker.start()
            except IndexError:
                self.logs.append(f"Error: Unable to find SerpStat ID for {location_name}.")

    def store_task_id(self, task_id):
        industry = getattr(self, "selected_industry", "Unknown Industry")
        self.task_industry_map[task_id] = industry
        self.logs.append(f"Task ID {task_id} stored with industry: {industry}")

    def write_task_ids_to_file(self):
        file_path = os.path.join(base_path, "current_task_ids.txt")
        try:
            with open(file_path, "w") as file:
                for task_id, industry in self.task_industry_map.items():
                    file.write(f"{task_id}, {industry}\n")
            self.logs.append(f"Task IDs written to {file_path}")
        except Exception as e:
            self.logs.append(f"Error writing task IDs: {e}")

    def on_worker_finished(self, worker):
        if worker in self.running_threads:
            self.running_threads.remove(worker)
        if not self.running_threads:
            self.write_task_ids_to_file()
            scripts = [
                "serp_crawl_data_return.py",
                "transformation_of_raw_data.py",
                "wiza_final_api_file.py",
                "combine_all_data_to_workbook.py"
            ]
            count = 0
            for script in scripts:
                script_path = os.path.join(base_path, script)
                count += 1
                try:
                    self.logs.append(f"Running {script}...")
                    subprocess.run(["python", script_path], check=True)
                    self.logs.append(f"Completed {script}")
                except subprocess.CalledProcessError as e:
                    self.logs.append(f"Error running {script}: {e}")
                    break
                except Exception as e:
                    self.logs.append(f"Unexpected error with {script}: {e}")
                    break
                if count >= 4:
                    sys.exit(app.exec_())
                else:
                    pass

        self.logs.append("Worker finished.")

    def closeEvent(self, event):
        self.write_task_ids_to_file()
        for worker in self.running_threads:
            worker.requestInterruption()
            worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerpstatApp()
    window.show()
    sys.exit(app.exec_())
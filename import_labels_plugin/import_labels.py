import pcbnew
import wx
import csv

class ImportNetLabels(pcbnew.ActionPlugin):
    def __init__(self):
        super(ImportNetLabels, self).__init__()
        self.name = "Import Net/Global/Hierarchical/Text Labels"
        self.category = "Schematic tools"
        self.description = "Import labels from a CSV or TXT file and place them in a grid"

    def defaults(self):
        self.name = "Import Labels with Options"
        self.category = "Label Tools"
        self.description = "Import and place labels from a CSV or TXT file"

    def Run(self):
        # Open a file dialog to choose the input file
        wildcard = "CSV files (*.csv)|*.csv|Text files (*.txt)|*.txt"
        dlg = wx.FileDialog(None, "Select Label File", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return  # User canceled

        # Get the file path
        file_path = dlg.GetPath()

        # Read the file and extract labels
        labels = self.read_labels(file_path)

        # Show options for label type and duplicate handling
        label_type, keep_duplicates = self.show_options_dialog()

        # Filter duplicates if needed
        if not keep_duplicates:
            labels = list(set(labels))

        # Create and place the labels in a grid layout
        self.create_labels_in_grid(label_type, labels)
        pcbnew.Refresh()

    def read_labels(self, file_path):
        labels = []
        try:
            if file_path.endswith(".csv"):
                with open(file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    labels = [row[0] for row in reader if row]  # Extract labels from column A
            elif file_path.endswith(".txt"):
                with open(file_path, "r") as txtfile:
                    labels = [line.strip() for line in txtfile if line.strip()]  # Read each line as a label
        except Exception as e:
            print(f"Error reading file: {e}")
        return labels

    def show_options_dialog(self):
        dialog = wx.Dialog(None, -1, "Label Import Options", size=(300, 200))
        panel = wx.Panel(dialog)
        
        label_choices = ["Net Label", "Global Label", "Hierarchical Label", "Text"]
        label_type_choice = wx.RadioBox(panel, label="Select Label Type", choices=label_choices, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        duplicate_checkbox = wx.CheckBox(panel, label="Keep Duplicates")
        duplicate_checkbox.SetValue(True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(label_type_choice, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(duplicate_checkbox, 0, wx.ALL | wx.CENTER, 5)
        button_sizer = wx.StdDialogButtonSizer()
        ok_button = wx.Button(dialog, wx.ID_OK)
        button_sizer.AddButton(ok_button)
        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)

        panel.SetSizer(sizer)
        result = dialog.ShowModal()
        
        label_type = label_type_choice.GetStringSelection()
        keep_duplicates = duplicate_checkbox.GetValue()
        dialog.Destroy()
        
        return label_type, keep_duplicates

    def create_labels_in_grid(self, label_type, labels):
        # Calculate spacing and initial position
        offset_x = 5  # Horizontal spacing in mm between labels
        offset_y = 5  # Vertical spacing in mm between labels
        rows = 10  # Number of labels per row before wrapping to a new row

        # Get the current schematic sheet
        sheet = pcbnew.GetCurrentSchematicSheet()
        if not sheet:
            print("No active schematic sheet found.")
            return

        # Prepare a list to hold the created labels
        created_labels = []

        for index, label in enumerate(labels):
            x_pos = (index % rows) * offset_x
            y_pos = (index // rows) * offset_y

            # Define the position for each label
            position = pcbnew.wxPointMM(10 + x_pos, 10 + y_pos)

            try:
                # Create the label based on the selected type
                if label_type == "Net Label":
                    new_label = sheet.AddNetLabel(label, position)
                elif label_type == "Global Label":
                    new_label = sheet.AddNetLabel(label, position)
                    new_label.IsGlobal = True
                elif label_type == "Hierarchical Label":
                    new_label = sheet.AddHierarchicalLabel(label, position)
                elif label_type == "Text":
                    new_label = sheet.AddText(label, position)

                created_labels.append(new_label)
                print(f"Created {label_type}: {label} at {position}.")
            except Exception as e:
                print(f"Failed to create label {label}: {e}")

        # Move all created labels together with the cursor for placement
        if created_labels:
            bounding_box = pcbnew.wxRect(
                min([label.GetX() for label in created_labels]),
                min([label.GetY() for label in created_labels]),
                max([label.GetX() for label in created_labels]),
                max([label.GetY() for label in created_labels])
            )
            sheet.MoveSelectionToCursor(bounding_box)

# Register the plugin
ImportNetLabels().register()

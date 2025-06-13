from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load and clean data
college_df = pd.read_csv("data/College List.csv")
allotment_df = pd.read_csv("data/Allotment List.csv")

# Clean 'Type' column in college_df
college_df['Type'] = college_df['Type'].astype(str).str.upper().str.strip().str.replace(r'\s+', ' ', regex=True)

# Define type mapping
type_mapping = {
    'UNIVERSITY': 'University',
    'GOVERNMENT COLLEGES': 'Government',
    'GOVERNMENT AIDED COLLEGES': 'Government Aided',
    'CONSTITUENT COLLEGES': 'Constituent',
    'PRIVATE COLLEGES': 'Private'
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=['POST', 'GET'])
def predict():
    if request.method == "POST":
        cutoff = float(request.form['cutoff'])
        community = request.form['community']

        
        filtered = allotment_df[allotment_df['COMMUNITY'] == community]
        eligible = filtered[filtered['CUTOFF'] <= cutoff]

        merged = pd.merge(eligible, college_df, left_on='COLLEGE CODE', right_on='Code', how='left')

        # Clean and map the type values
        merged['Type'] = merged['Type'].astype(str).str.upper().str.strip().str.replace(r'\s+', ' ', regex=True)
        merged['Type'] = merged['Type'].map(type_mapping)

        merged['Type'] = merged['Type'].fillna('Unknown')

       
        grouped = merged.groupby(['Type', 'Name '])['BRANCH CODE'].apply(
            lambda x: ', '.join(sorted(set(x)))
        ).reset_index()

        grouped.rename(columns={'BRANCH CODE': 'Branches'}, inplace=True)

        ordered_types = ['University','Government','Government Aided', 'Constituent', 'Private',   'Unknown']
        grouped['Type'] = pd.Categorical(grouped['Type'], categories=ordered_types, ordered=True)
        grouped.sort_values(['Type', 'Name '], inplace=True)

        return render_template("result.html", tables=grouped.to_html(index=False, classes='table'))

    return render_template("index.html")

if __name__ == "__main__":
    from os import environ
    app.run(host='0.0.0.0', port=int(environ.get("PORT", 5000)))

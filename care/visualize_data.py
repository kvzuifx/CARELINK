import pandas as pd
from django.core.management.base import BaseCommand
from matplotlib import pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from .models import Supply, Donation

class Command(BaseCommand):
    help = 'Generate and save data visualizations'

    def handle(self, *args, **options):
        self.generate_visualizations()

    def generate_visualizations(self):
        # Fetch data from Django models
        supply_data = Supply.objects.values('supply_category', 'supply_quantity')
        donation_data = Donation.objects.values('donor__ben_name', 'quantity_donated')

        # Convert to DataFrame
        supply_df = pd.DataFrame(supply_data)
        donation_df = pd.DataFrame(donation_data)
        
        # Convert quantity columns to numeric
        supply_df['supply_quantity'] = pd.to_numeric(supply_df['supply_quantity'], errors='coerce')
        donation_df['quantity_donated'] = pd.to_numeric(donation_df['quantity_donated'], errors='coerce')

        # Pie Chart for Supply Categories
        plt.figure(figsize=(12, 8))
        supply_category_totals = supply_df.groupby('supply_category')['supply_quantity'].sum().reset_index()
        colors = sns.color_palette('pastel', len(supply_category_totals))  # Custom colors
        wedges, texts, autotexts = plt.pie(
            supply_category_totals['supply_quantity'],
            labels=supply_category_totals['supply_category'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=140,  # Rotate the start angle
            shadow=True,  # Add shadow for better aesthetics
            explode=[0.1] * len(supply_category_totals)  # Explode each slice for emphasis
        )
        plt.title('Supply Categories Distribution')

        # Customize label and percentage font sizes
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(10)

        # Add a legend
        plt.legend(
            wedges,
            supply_category_totals['supply_category'],
            title="Supply Categories",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1)
        )

        # Save pie chart to a BytesIO object
        pie_img = BytesIO()
        plt.savefig(pie_img, format='png', bbox_inches='tight')  # Adjust bbox_inches to fit the legend
        plt.close()

        # Encode image to base64
        pie_img_base64 = base64.b64encode(pie_img.getvalue()).decode()
        
        # Bar Graph for Donations by Donor
        plt.figure(figsize=(12, 6))
        plt.bar(donation_df['donor__ben_name'], donation_df['quantity_donated'], color=sns.color_palette('viridis', len(donation_df)))
        plt.xlabel('Donor Name')
        plt.ylabel('Quantity Donated')
        plt.title('Total Donations by Donor')
        plt.xticks(rotation=90)

        # Save bar chart to a BytesIO object
        bar_img = BytesIO()
        plt.savefig(bar_img, format='png')
        plt.close()

        # Encode image to base64
        bar_img_base64 = base64.b64encode(bar_img.getvalue()).decode()

        # Output base64 strings for use in HTML
        self.stdout.write(self.style.SUCCESS(f'Pie Chart (Base64): {pie_img_base64}'))
        self.stdout.write(self.style.SUCCESS(f'Bar Chart (Base64): {bar_img_base64}'))

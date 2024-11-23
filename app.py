import pandas as pd
import gradio as gr
from utils import calculate_price_type_a, calculate_price_type_b

MAX_ITEMS = 10  # Maximum number of items allowed


def calculate_estimates(type_a_inputs, type_b_inputs):
    # Prepare data for display
    results = []
    for idx, item in enumerate(type_a_inputs):
        if item["Total Exposed Area (Carcass)"] > 0:
            price = calculate_price_type_a(item)
            results.append(
                {
                    "Item Type": "Type A",
                    "Item Number": idx + 1,
                    "Price": price,  # Store as number
                    "Price Display": f"₹{price:.2f}",  # Store formatted string separately
                    "Details": f"Carcass Area: {item['Total Exposed Area (Carcass)']} sq.ft, Shutter Area: {item['Shutter Area']} sq.ft",
                }
            )
    for idx, item in enumerate(type_b_inputs):
        if item["Total Area"] > 0:
            price = calculate_price_type_b(item)
            results.append(
                {
                    "Item Type": "Type B",
                    "Item Number": idx + 1,
                    "Price": price,  # Store as number
                    "Price Display": f"₹{price:.2f}",  # Store formatted string separately
                    "Details": f"Total Area: {item['Total Area']} sq.ft, Finish: {item['Finish']}",
                }
            )

    df = pd.DataFrame(results)
    if not df.empty:
        # Calculate total
        total_price = df["Price"].sum()
        total_row = pd.DataFrame(
            [
                {
                    "Item Type": "TOTAL",
                    "Item Number": None,  # Use None for proper sorting
                    "Price": total_price,
                    "Price Display": f"₹{total_price:.2f}",
                    "Details": "",
                }
            ]
        )
        df = pd.concat([df, total_row], ignore_index=True)

        # Prepare final display DataFrame
        display_df = df[["Item Type", "Item Number", "Price Display", "Details"]].copy()
        display_df.columns = [
            "Item Type",
            "Item Number",
            "Price",
            "Details",
        ]  # Rename for display

        # Set proper data types
        display_df["Item Number"] = pd.to_numeric(
            display_df["Item Number"], errors="ignore"
        )

        return display_df
    return pd.DataFrame(columns=["Item Type", "Item Number", "Price", "Details"])


def on_calculate(num_type_a, num_type_b, *args):
    idx = 0
    num_type_a = int(num_type_a)
    num_type_b = int(num_type_b)
    type_a_inputs = []
    number_of_inputs_per_type_a_item = 9
    number_of_inputs_per_type_b_item = 2
    for _ in range(num_type_a):
        item = {
            "Total Exposed Area (Carcass)": args[idx],
            "Total Internal Area (Carcass)": args[idx + 1],
            "External Finish": args[idx + 2],
            "External Category": args[idx + 3],
            "Internal Finish": args[idx + 4],
            "Internal Category": args[idx + 5],
            "Shutter Area": args[idx + 6],
            "Shutter Finish": args[idx + 7],
            "Shutter Category": args[idx + 8],
        }
        type_a_inputs.append(item)
        idx += number_of_inputs_per_type_a_item
    # Skip remaining Type A inputs
    idx += (MAX_ITEMS - num_type_a) * number_of_inputs_per_type_a_item
    type_b_inputs = []
    for _ in range(num_type_b):
        item = {"Total Area": args[idx], "Finish": args[idx + 1]}
        type_b_inputs.append(item)
        idx += number_of_inputs_per_type_b_item
    # Skip remaining Type B inputs
    results = calculate_estimates(type_a_inputs, type_b_inputs)
    return results


def update_type_a_visibility(num_items):
    num_items = int(num_items)
    updates = []
    for i in range(MAX_ITEMS):
        updates.append(gr.update(visible=i < num_items))
    return updates


def update_type_b_visibility(num_items):
    num_items = int(num_items)
    updates = []
    for i in range(MAX_ITEMS):
        updates.append(gr.update(visible=i < num_items))
    return updates


with gr.Blocks() as demo:
    gr.Markdown("# 🛠️ Furniture Quotation Calculator")

    with gr.Row():
        num_type_a_items = gr.Number(
            label="Number of Type A Items",
            value=1,
            precision=0,
            minimum=0,
            maximum=MAX_ITEMS,
        )
        num_type_b_items = gr.Number(
            label="Number of Type B Items",
            value=1,
            precision=0,
            minimum=0,
            maximum=MAX_ITEMS,
        )

    # Type A Items
    type_a_items = []
    type_a_groups = []
    with gr.Tab("Type A: Wardrobes and Units"):
        for i in range(MAX_ITEMS):
            with gr.Group(visible=(i == 0)) as group:
                gr.Markdown(f"### Type A Item {i + 1}")
                # Define input components
                total_exposed_area = gr.Number(
                    label="Total Exposed Area (Carcass) (sq.ft)", value=0
                )
                total_internal_area = gr.Number(
                    label="Total Internal Area (Carcass)(sq.ft)", value=0
                )

                with gr.Row():
                    external_finish = gr.Dropdown(
                        label="External Finish",
                        choices=["Laminate", "PU", "Duco"],
                    )
                    external_category = gr.Dropdown(
                        label="External Category",
                        choices=["Budget", "Mainstream", "Premium"],
                    )

                with gr.Row():
                    internal_finish = gr.Dropdown(
                        label="Internal Finish",
                        choices=["Laminate", "PU", "Duco"],
                    )
                    internal_category = gr.Dropdown(
                        label="Internal Category",
                        choices=["Budget", "Mainstream", "Premium"],
                    )

                shutter_area = gr.Number(label="Shutter Area (sq.ft)", value=0)

                with gr.Row():
                    shutter_finish = gr.Dropdown(
                        label="Shutter Finish",
                        choices=["Laminate", "Acrylic", "PU", "Duco"],
                    )
                    shutter_category = gr.Dropdown(
                        label="Shutter Category",
                        choices=["Budget", "Mainstream", "Premium"],
                    )

                type_a_items.append(
                    {
                        "Total Exposed Area (Carcass)": total_exposed_area,
                        "Total Internal Area (Carcass)": total_internal_area,
                        "External Finish": external_finish,
                        "External Category": external_category,
                        "Internal Finish": internal_finish,
                        "Internal Category": internal_category,
                        "Shutter Category": shutter_category,
                        "Shutter Area": shutter_area,
                        "Shutter Finish": shutter_finish,
                    }
                )
                type_a_groups.append(group)

    # Type B Items
    type_b_items = []
    type_b_groups = []
    with gr.Tab("Type B: Wall Decor"):
        for i in range(MAX_ITEMS):
            with gr.Group(visible=(i == 0)) as group:
                gr.Markdown(f"### Type B Item {i + 1}")
                total_area = gr.Number(label="Total Area (sq.ft)", value=0)
                finish = gr.Dropdown(label="Finish", choices=["Laminate", "PU", "Duco"])
                type_b_items.append({"Total Area": total_area, "Finish": finish})
                type_b_groups.append(group)

    # Connect the number inputs to visibility update functions
    num_type_a_items.change(
        update_type_a_visibility, inputs=[num_type_a_items], outputs=type_a_groups
    )

    num_type_b_items.change(
        update_type_b_visibility, inputs=[num_type_b_items], outputs=type_b_groups
    )

    # Calculation Button and Output
    calculate_btn = gr.Button("Calculate Estimates")
    output = gr.DataFrame(
        headers=["Item Type", "Item Number", "Price", "Details"],
        datatype=["str", "number", "str", "str"],
        label="Estimated Prices",
        wrap=True,
        column_widths=["100px", "100px", "150px", "400px"],
    )

    # Collect all inputs
    inputs = [num_type_a_items, num_type_b_items]
    for item in type_a_items:
        inputs.extend(
            [
                item["Total Exposed Area (Carcass)"],
                item["Total Internal Area (Carcass)"],
                item["External Finish"],
                item["External Category"],
                item["Internal Finish"],
                item["Internal Category"],
                item["Shutter Area"],
                item["Shutter Finish"],
                item["Shutter Category"],
            ]
        )
    for item in type_b_items:
        inputs.extend([item["Total Area"], item["Finish"]])

    # Connect the calculation function
    calculate_btn.click(on_calculate, inputs=inputs, outputs=output)

demo.launch()


import csv
import networkx as nx

G = nx.DiGraph()

# Load 2025 supply chain graph
with open("data/supply_relationships.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        if int(row["year"]) == 2025:
            G.add_edge(row["supplier_id"], row["customer_id"])


def simulate_disruption(G, failed_supplier):

    affected = {failed_supplier}

    changed = True

    while changed:
        changed = False
        candidates = set()

        for supplier in affected:
            candidates.update(G.successors(supplier))

        for customer in candidates:

            if customer in affected:
                continue

            suppliers = set(G.predecessors(customer))

            if suppliers and suppliers.issubset(affected):
                affected.add(customer)
                changed = True

    direct_customers = set(G.successors(failed_supplier))

    # Direct customers with no alternative recorded supplier
    direct_affected = {
        customer
        for customer in direct_customers
        if set(G.predecessors(customer)) == {failed_supplier}
    }

    
    cascading_affected = len(affected) - 1 - len(direct_affected)

    total_affected = len(affected) - 1

    # Calculate risk indicators
    direct_dependency_rate = (
        len(direct_affected) / len(direct_customers) * 100
        if direct_customers else 0
    )

    cascading_impact_rate = (
        cascading_affected / total_affected * 100
        if total_affected else 0
    )

    return {
        "supplier_id": failed_supplier.split(":")[-1],
        "direct_customers": len(direct_customers),
        "directly_affected": len(direct_affected),
        "direct_dependency_rate": round(direct_dependency_rate, 2),
        "cascading_affected": cascading_affected,
        "cascading_impact_rate": round(cascading_impact_rate, 2),
        "total_affected": total_affected
    }


# Select top 10 suppliers by direct customer count
top_suppliers = sorted(
    G.out_degree(),
    key=lambda x: x[1],
    reverse=True
)[:10]

results = []

for supplier, degree in top_suppliers:
    results.append(simulate_disruption(G, supplier))


# Rank suppliers by total simulated impact
results.sort(
    key=lambda x: x["total_affected"],
    reverse=True
)


# Display results
print("\nSUPPLIER DISRUPTION RISK COMPARISON")
print("=" * 100)

for result in results:
    print(
        f"Supplier: {result['supplier_id']} | "
        f"Direct: {result['direct_customers']} | "
        f"Directly affected: {result['directly_affected']} | "
        f"Dependency rate: {result['direct_dependency_rate']}% | "
        f"Cascading: {result['cascading_affected']} | "
        f"Cascade rate: {result['cascading_impact_rate']}% | "
        f"Total: {result['total_affected']}"
    )


# Export results to CSV
output_file = "data/supplier_risk_comparison.csv"

fieldnames = [
    "supplier_id",
    "direct_customers",
    "directly_affected",
    "direct_dependency_rate",
    "cascading_affected",
    "cascading_impact_rate",
    "total_affected"
]

with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(results)

print("\nCSV EXPORT COMPLETED!")
print(f"Results saved to: {output_file}")
print(f"Total suppliers analyzed: {len(results)}")

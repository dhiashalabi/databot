"""File generation tools for MCP server - PDF, CSV, Excel exports."""

from pathlib import Path
from typing import Any
import uuid

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select

from src.models.customer import Customer
from src.models.product import Category, Product
from src.models.sales import Sale

from .base_tools import BaseTools


class FileTools(BaseTools):
	"""File generation tools for exporting data in various formats."""

	def __init__(self, db):
		"""Initialize file tools with database session."""
		super().__init__(db)
		self.exports_dir = Path("static/exports")
		self.exports_dir.mkdir(parents=True, exist_ok=True)

	def _generate_filename(self, export_type: str, data_type: str) -> tuple[str, str]:
		"""Generate unique filename and return both filename and full path."""
		file_id = str(uuid.uuid4())
		filename = f"{data_type}_{file_id}.{export_type}"
		file_path = self.exports_dir / filename
		return filename, str(file_path)

	async def export_sales_to_csv(
		self,
		start_date: str | None = None,
		end_date: str | None = None,
		include_details: bool = True,
	) -> dict[str, Any]:
		"""Export sales data to CSV format."""
		try:
			await self.db.rollback()

			query = select(
				Sale.id,
				Sale.sale_date,
				Sale.amount.label("total_amount"),
				Sale.quantity,
				Sale.sales_channel.label("sale_type"),
				Sale.customer_name,
				Customer.email.label("customer_email"),
				Sale.product_name,
				Sale.category.label("product_category"),
				Product.unit_price.label("product_price"),
			).select_from(
				Sale.__table__.outerjoin(
					Customer.__table__, Sale.customer_id == Customer.id
				).outerjoin(Product.__table__, Sale.product_id == Product.id)
			)

			if start_date:
				query = query.where(Sale.sale_date >= start_date)

			if end_date:
				query = query.where(Sale.sale_date <= end_date)

			query = query.order_by(Sale.sale_date.desc())

			result = await self.db.execute(query)
			data = result.fetchall()

			if not data:
				return {
					"success": False,
					"message": "No sales data found for the specified criteria",
				}

			df = pd.DataFrame([dict(row._mapping) for row in data])

			filename, file_path = self._generate_filename("csv", "sales_export")

			df.to_csv(file_path, index=False)

			return {
				"success": True,
				"message": "Sales data exported successfully to CSV",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(data),
				"columns": list(df.columns),
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting sales to CSV: {str(e)}",
			}

	async def export_customers_to_csv(
		self, customer_type: str | None = None, include_sales_summary: bool = True
	) -> dict[str, Any]:
		"""Export customers data to CSV format."""
		try:
			await self.db.rollback()

			if include_sales_summary:
				sales_summary = (
					select(
						Sale.customer_id,
						func.sum(Sale.amount).label("total_sales"),
						func.count(Sale.id).label("total_orders"),
						func.avg(Sale.amount).label("avg_order_value"),
					)
					.group_by(Sale.customer_id)
					.subquery()
				)

				query = select(
					Customer.id,
					Customer.customer_name.label("name"),
					Customer.email,
					Customer.phone,
					Customer.address,
					Customer.city,
					Customer.customer_type,
					Customer.created_at,
					func.coalesce(sales_summary.c.total_sales, 0).label("total_sales"),
					func.coalesce(sales_summary.c.total_orders, 0).label(
						"total_orders"
					),
					func.coalesce(sales_summary.c.avg_order_value, 0).label(
						"avg_order_value"
					),
				).select_from(
					Customer.__table__.outerjoin(
						sales_summary, Customer.id == sales_summary.c.customer_id
					)
				)
			else:
				query = select(
					Customer.id,
					Customer.customer_name.label("name"),
					Customer.email,
					Customer.phone,
					Customer.address,
					Customer.city,
					Customer.customer_type,
					Customer.created_at,
				)

			if customer_type:
				query = query.where(Customer.customer_type == customer_type)

			query = query.order_by(Customer.customer_name)

			result = await self.db.execute(query)
			data = result.fetchall()

			if not data:
				return {"success": False, "message": "No customer data found"}

			df = pd.DataFrame([dict(row._mapping) for row in data])
			filename, file_path = self._generate_filename("csv", "customers_export")
			df.to_csv(file_path, index=False)

			return {
				"success": True,
				"message": "Customer data exported successfully to CSV",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(data),
				"columns": list(df.columns),
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting customers to CSV: {str(e)}",
			}

	async def export_products_to_excel(
		self, category: str | None = None, include_sales_data: bool = True
	) -> dict[str, Any]:
		"""Export products data to Excel format with multiple sheets."""
		try:
			await self.db.rollback()

			products_query = select(
				Product.id,
				Product.product_name.label("name"),
				Category.category_name.label("category"),
				Product.unit_price.label("price"),
				Product.stock_quantity,
				Product.description,
				Product.created_at,
			).select_from(
				Product.__table__.outerjoin(
					Category.__table__, Product.category_id == Category.id
				)
			)

			if category:
				products_query = products_query.where(
					Category.category_name == category
				)

			products_query = products_query.order_by(Product.product_name)

			result = await self.db.execute(products_query)
			products_data = result.fetchall()

			if not products_data:
				return {"success": False, "message": "No product data found"}

			filename, file_path = self._generate_filename("xlsx", "products_export")

			with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
				products_df = pd.DataFrame(
					[dict(row._mapping) for row in products_data]
				)
				products_df.to_excel(writer, sheet_name="Products", index=False)

				if include_sales_data:
					sales_query = select(
						Product.product_name,
						Category.category_name.label("category"),
						func.sum(Sale.quantity).label("total_quantity_sold"),
						func.sum(Sale.amount).label("total_revenue"),
						func.count(Sale.id).label("total_orders"),
						func.avg(Sale.amount).label("avg_order_value"),
					).select_from(
						Product.__table__.outerjoin(
							Category.__table__, Product.category_id == Category.id
						).outerjoin(Sale.__table__, Product.id == Sale.product_id)
					)

					if category:
						sales_query = sales_query.where(
							Category.category_name == category
						)

					sales_query = sales_query.group_by(
						Product.id, Product.product_name, Category.category_name
					).order_by(func.sum(Sale.amount).desc())

					sales_result = await self.db.execute(sales_query)
					sales_data = sales_result.fetchall()

					if sales_data:
						sales_df = pd.DataFrame(
							[dict(row._mapping) for row in sales_data]
						)
						sales_df.to_excel(
							writer, sheet_name="Sales Summary", index=False
						)

			return {
				"success": True,
				"message": "Product data exported successfully to Excel",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(products_data),
				"sheets": ["Products", "Sales Summary"]
				if include_sales_data
				else ["Products"],
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting products to Excel: {str(e)}",
			}

	async def export_sales_report_to_pdf(
		self,
		start_date: str | None = None,
		end_date: str | None = None,
		report_title: str = "Sales Report",
	) -> dict[str, Any]:
		"""Export sales report to PDF format with formatted layout."""
		try:
			await self.db.rollback()

			query = select(
				Sale.sale_date,
				Sale.amount.label("total_amount"),
				Sale.quantity,
				Sale.sales_channel.label("sale_type"),
				Sale.customer_name,
				Sale.product_name,
				Sale.category.label("product_category"),
			).select_from(
				Sale.__table__.outerjoin(
					Customer.__table__, Sale.customer_id == Customer.id
				).outerjoin(Product.__table__, Sale.product_id == Product.id)
			)

			if start_date:
				query = query.where(Sale.sale_date >= start_date)

			if end_date:
				query = query.where(Sale.sale_date <= end_date)

			query = query.order_by(Sale.sale_date.desc()).limit(100)

			result = await self.db.execute(query)
			sales_data = result.fetchall()

			if not sales_data:
				return {
					"success": False,
					"message": "No sales data found for the specified period",
				}

			summary_query = select(
				func.count(Sale.id).label("total_orders"),
				func.sum(Sale.amount).label("total_revenue"),
				func.avg(Sale.amount).label("avg_order_value"),
				func.sum(Sale.quantity).label("total_items_sold"),
			)

			if start_date:
				summary_query = summary_query.where(Sale.sale_date >= start_date)

			if end_date:
				summary_query = summary_query.where(Sale.sale_date <= end_date)

			summary_result = await self.db.execute(summary_query)
			summary_data = summary_result.fetchone()

			filename, file_path = self._generate_filename("pdf", "sales_report")

			doc = SimpleDocTemplate(file_path, pagesize=A4)
			styles = getSampleStyleSheet()
			story = []

			title_style = ParagraphStyle(
				"CustomTitle",
				parent=styles["Heading1"],
				fontSize=18,
				spaceAfter=30,
				alignment=1,
			)
			story.append(Paragraph(report_title, title_style))
			story.append(Spacer(1, 20))

			summary_style = styles["Heading2"]
			story.append(Paragraph("Summary", summary_style))
			story.append(Spacer(1, 10))

			if summary_data:
				summary_text = f"""
				<b>Total Orders:</b> {summary_data.total_orders}<br/>
				<b>Total Revenue:</b> ${summary_data.total_revenue:,.2f}<br/>
				<b>Average Order Value:</b> ${summary_data.avg_order_value:,.2f}<br/>
				<b>Total Items Sold:</b> {summary_data.total_items_sold}
				"""
			else:
				summary_text = """
				<b>Total Orders:</b> 0<br/>
				<b>Total Revenue:</b> $0.00<br/>
				<b>Average Order Value:</b> $0.00<br/>
				<b>Total Items Sold:</b> 0
				"""
			story.append(Paragraph(summary_text, styles["Normal"]))
			story.append(Spacer(1, 20))

			story.append(Paragraph("Sales Details", summary_style))
			story.append(Spacer(1, 10))

			table_data = [
				["Date", "Customer", "Product", "Category", "Amount", "Qty", "Type"]
			]

			for row in sales_data[:50]:
				table_data.append(
					[
						str(row.sale_date),
						row.customer_name or "N/A",
						row.product_name or "N/A",
						row.product_category or "N/A",
						f"${row.total_amount:.2f}",
						str(row.quantity),
						row.sale_type or "N/A",
					]
				)

			table = Table(table_data)
			table.setStyle(
				TableStyle(
					[
						("BACKGROUND", (0, 0), (-1, 0), colors.grey),
						("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
						("ALIGN", (0, 0), (-1, -1), "CENTER"),
						("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
						("FONTSIZE", (0, 0), (-1, 0), 10),
						("BOTTOMPADDING", (0, 0), (-1, 0), 12),
						("BACKGROUND", (0, 1), (-1, -1), colors.beige),
						("FONTSIZE", (0, 1), (-1, -1), 8),
						("GRID", (0, 0), (-1, -1), 1, colors.black),
					]
				)
			)

			story.append(table)
			doc.build(story)

			summary = {}
			if summary_data:
				summary = {
					"total_orders": summary_data.total_orders,
					"total_revenue": float(summary_data.total_revenue),
					"avg_order_value": float(summary_data.avg_order_value),
					"total_items_sold": summary_data.total_items_sold,
				}
			else:
				summary = {
					"total_orders": 0,
					"total_revenue": 0.0,
					"avg_order_value": 0.0,
					"total_items_sold": 0,
				}

			return {
				"success": True,
				"message": "Sales report exported successfully to PDF",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(sales_data),
				"summary": summary,
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting sales report to PDF: {str(e)}",
			}

	async def export_customers_to_pdf(
		self,
		customer_type: str | None = None,
		limit: int | None = None,
		report_title: str = "Customer Report",
		include_sales_summary: bool = True,
	) -> dict[str, Any]:
		"""Export customers data to PDF format with formatted layout."""
		try:
			await self.db.rollback()

			if include_sales_summary:
				sales_summary = (
					select(
						Sale.customer_id,
						func.sum(Sale.amount).label("total_sales"),
						func.count(Sale.id).label("total_orders"),
						func.avg(Sale.amount).label("avg_order_value"),
						func.max(Sale.sale_date).label("last_purchase"),
					)
					.group_by(Sale.customer_id)
					.subquery()
				)

				query = select(
					Customer.id,
					Customer.customer_name.label("name"),
					Customer.email,
					Customer.phone,
					Customer.address,
					Customer.city,
					Customer.customer_type,
					Customer.created_at,
					func.coalesce(sales_summary.c.total_sales, 0).label("total_sales"),
					func.coalesce(sales_summary.c.total_orders, 0).label(
						"total_orders"
					),
					func.coalesce(sales_summary.c.avg_order_value, 0).label(
						"avg_order_value"
					),
					sales_summary.c.last_purchase,
				).select_from(
					Customer.__table__.outerjoin(
						sales_summary, Customer.id == sales_summary.c.customer_id
					)
				)
			else:
				query = select(
					Customer.id,
					Customer.customer_name.label("name"),
					Customer.email,
					Customer.phone,
					Customer.address,
					Customer.city,
					Customer.customer_type,
					Customer.created_at,
				)

			if customer_type:
				query = query.where(Customer.customer_type == customer_type)

			if include_sales_summary:
				query = query.order_by(
					func.coalesce(sales_summary.c.total_sales, 0).desc()
				)
			else:
				query = query.order_by(Customer.customer_name)

			if limit:
				query = query.limit(limit)

			result = await self.db.execute(query)
			customer_data = result.fetchall()

			if not customer_data:
				return {
					"success": False,
					"message": "No customer data found for the specified criteria",
				}

			if include_sales_summary:
				total_customers = len(customer_data)
				total_revenue = sum(float(row.total_sales) for row in customer_data)
				total_orders = sum(int(row.total_orders) for row in customer_data)
				avg_customer_value = (
					total_revenue / total_customers if total_customers else 0
				)
			else:
				total_customers = len(customer_data)
				total_revenue = 0
				total_orders = 0
				avg_customer_value = 0

			filename, file_path = self._generate_filename("pdf", "customers_report")

			doc = SimpleDocTemplate(file_path, pagesize=A4)
			styles = getSampleStyleSheet()
			story = []

			title_style = ParagraphStyle(
				"CustomTitle",
				parent=styles["Heading1"],
				fontSize=18,
				spaceAfter=30,
				alignment=1,
			)
			story.append(Paragraph(report_title, title_style))
			story.append(Spacer(1, 20))

			summary_style = styles["Heading2"]
			story.append(Paragraph("Summary", summary_style))
			story.append(Spacer(1, 10))

			summary_text = f"""
			<b>Total Customers:</b> {total_customers}<br/>
			<b>Total Revenue:</b> ${total_revenue:,.2f}<br/>
			<b>Total Orders:</b> {total_orders}<br/>
			<b>Average Customer Value:</b> ${avg_customer_value:,.2f}
			"""
			story.append(Paragraph(summary_text, styles["Normal"]))
			story.append(Spacer(1, 20))

			story.append(Paragraph("Customer Details", summary_style))
			story.append(Spacer(1, 10))

			if include_sales_summary:
				table_data = [
					[
						"Name",
						"Email",
						"Type",
						"City",
						"Total Sales",
						"Orders",
						"Avg Order",
					]
				]

				for row in customer_data[:50]:
					table_data.append(
						[
							row.name or "N/A",
							row.email or "N/A",
							row.customer_type or "N/A",
							row.city or "N/A",
							f"${float(row.total_sales):,.2f}",
							str(row.total_orders),
							f"${float(row.avg_order_value):,.2f}",
						]
					)
			else:
				table_data = [["Name", "Email", "Type", "City", "Phone", "Address"]]

				for row in customer_data[:50]:
					table_data.append(
						[
							row.name or "N/A",
							row.email or "N/A",
							row.customer_type or "N/A",
							row.city or "N/A",
							row.phone or "N/A",
							row.address or "N/A",
						]
					)

			table = Table(table_data)
			table.setStyle(
				TableStyle(
					[
						("BACKGROUND", (0, 0), (-1, 0), colors.grey),
						("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
						("ALIGN", (0, 0), (-1, -1), "CENTER"),
						("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
						("FONTSIZE", (0, 0), (-1, 0), 9),
						("BOTTOMPADDING", (0, 0), (-1, 0), 12),
						("BACKGROUND", (0, 1), (-1, -1), colors.beige),
						("FONTSIZE", (0, 1), (-1, -1), 7),
						("GRID", (0, 0), (-1, -1), 1, colors.black),
					]
				)
			)

			story.append(table)
			doc.build(story)

			return {
				"success": True,
				"message": "Customer report exported successfully to PDF",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(customer_data),
				"summary": {
					"total_customers": total_customers,
					"total_revenue": total_revenue,
					"total_orders": total_orders,
					"avg_customer_value": avg_customer_value,
				},
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting customers to PDF: {str(e)}",
			}

	async def export_top_customers_to_pdf(
		self,
		limit: int = 10,
		metric: str = "revenue",
		report_title: str | None = None,
	) -> dict[str, Any]:
		"""Export top customers to PDF format based on revenue or order count."""
		try:
			await self.db.rollback()

			if not report_title:
				if metric == "orders":
					report_title = f"Top {limit} Customers by Order Count"
				else:
					report_title = f"Top {limit} Customers by Revenue"

			sales_summary = (
				select(
					Sale.customer_id,
					func.sum(Sale.amount).label("total_sales"),
					func.count(Sale.id).label("total_orders"),
					func.avg(Sale.amount).label("avg_order_value"),
					func.max(Sale.sale_date).label("last_purchase"),
				)
				.group_by(Sale.customer_id)
				.subquery()
			)

			query = select(
				Customer.id,
				Customer.customer_name.label("name"),
				Customer.email,
				Customer.phone,
				Customer.city,
				Customer.customer_type,
				func.coalesce(sales_summary.c.total_sales, 0).label("total_sales"),
				func.coalesce(sales_summary.c.total_orders, 0).label("total_orders"),
				func.coalesce(sales_summary.c.avg_order_value, 0).label(
					"avg_order_value"
				),
				sales_summary.c.last_purchase,
			).select_from(
				Customer.__table__.join(
					sales_summary, Customer.id == sales_summary.c.customer_id
				)
			)

			if metric == "orders":
				query = query.order_by(sales_summary.c.total_orders.desc())
			else:
				query = query.order_by(sales_summary.c.total_sales.desc())

			query = query.limit(limit)

			result = await self.db.execute(query)
			customer_data = result.fetchall()

			if not customer_data:
				return {
					"success": False,
					"message": "No customer data found with sales history",
				}

			total_customers = len(customer_data)
			total_revenue = sum(float(row.total_sales) for row in customer_data)
			total_orders = sum(int(row.total_orders) for row in customer_data)
			avg_customer_value = (
				total_revenue / total_customers if total_customers else 0
			)

			filename, file_path = self._generate_filename("pdf", "top_customers_report")

			doc = SimpleDocTemplate(file_path, pagesize=A4)
			styles = getSampleStyleSheet()
			story = []

			title_style = ParagraphStyle(
				"CustomTitle",
				parent=styles["Heading1"],
				fontSize=18,
				spaceAfter=30,
				alignment=1,
			)
			story.append(Paragraph(report_title, title_style))
			story.append(Spacer(1, 20))

			summary_style = styles["Heading2"]
			story.append(Paragraph("Summary", summary_style))
			story.append(Spacer(1, 10))

			summary_text = f"""
			<b>Top {limit} Customers ({metric.title()}):</b> {total_customers}<br/>
			<b>Combined Revenue:</b> ${total_revenue:,.2f}<br/>
			<b>Combined Orders:</b> {total_orders}<br/>
			<b>Average Customer Value:</b> ${avg_customer_value:,.2f}
			"""
			story.append(Paragraph(summary_text, styles["Normal"]))
			story.append(Spacer(1, 20))

			story.append(Paragraph("Customer Details", summary_style))
			story.append(Spacer(1, 10))

			table_data = [
				[
					"Rank",
					"Name",
					"Email",
					"City",
					"Type",
					"Total Sales",
					"Orders",
					"Avg Order",
					"Last Purchase",
				]
			]

			for i, row in enumerate(customer_data, 1):
				last_purchase = (
					str(row.last_purchase)[:10] if row.last_purchase else "N/A"
				)
				table_data.append(
					[
						str(i),
						row.name or "N/A",
						row.email or "N/A",
						row.city or "N/A",
						row.customer_type or "N/A",
						f"${float(row.total_sales):,.2f}",
						str(row.total_orders),
						f"${float(row.avg_order_value):,.2f}",
						last_purchase,
					]
				)

			table = Table(table_data)
			table.setStyle(
				TableStyle(
					[
						("BACKGROUND", (0, 0), (-1, 0), colors.grey),
						("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
						("ALIGN", (0, 0), (-1, -1), "CENTER"),
						("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
						("FONTSIZE", (0, 0), (-1, 0), 8),
						("BOTTOMPADDING", (0, 0), (-1, 0), 12),
						("BACKGROUND", (0, 1), (-1, -1), colors.beige),
						("FONTSIZE", (0, 1), (-1, -1), 6),
						("GRID", (0, 0), (-1, -1), 1, colors.black),
					]
				)
			)

			story.append(table)
			doc.build(story)

			return {
				"success": True,
				"message": f"Top {limit} customers report exported successfully to PDF",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(customer_data),
				"metric": metric,
				"summary": {
					"total_customers": total_customers,
					"total_revenue": total_revenue,
					"total_orders": total_orders,
					"avg_customer_value": avg_customer_value,
				},
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting top customers to PDF: {str(e)}",
			}

	async def export_products_to_pdf(
		self,
		category: str | None = None,
		limit: int | None = None,
		report_title: str = "Products Report",
		include_sales_data: bool = True,
	) -> dict[str, Any]:
		"""Export products data to PDF format with formatted layout."""
		try:
			await self.db.rollback()

			products_query = select(
				Product.id,
				Product.product_name.label("name"),
				Category.category_name.label("category"),
				Product.unit_price.label("price"),
				Product.stock_quantity,
				Product.description,
				Product.created_at,
			).select_from(
				Product.__table__.outerjoin(
					Category.__table__, Product.category_id == Category.id
				)
			)

			if category:
				products_query = products_query.where(
					Category.category_name == category
				)

			products_query = products_query.order_by(Product.product_name)

			if limit:
				products_query = products_query.limit(limit)

			result = await self.db.execute(products_query)
			products_data = result.fetchall()

			if not products_data:
				return {"success": False, "message": "No product data found"}

			sales_data = []
			if include_sales_data:
				sales_query = select(
					Product.product_name,
					Category.category_name.label("category"),
					func.sum(Sale.quantity).label("total_quantity_sold"),
					func.sum(Sale.amount).label("total_revenue"),
					func.count(Sale.id).label("total_orders"),
					func.avg(Sale.amount).label("avg_order_value"),
				).select_from(
					Product.__table__.outerjoin(
						Category.__table__, Product.category_id == Category.id
					).outerjoin(Sale.__table__, Product.id == Sale.product_id)
				)

				if category:
					sales_query = sales_query.where(Category.category_name == category)

				sales_query = sales_query.group_by(
					Product.id, Product.product_name, Category.category_name
				).order_by(func.sum(Sale.amount).desc())

				if limit:
					sales_query = sales_query.limit(limit)

				sales_result = await self.db.execute(sales_query)
				sales_data = sales_result.fetchall()

			total_products = len(products_data)
			total_value = sum(
				float(row.price) * int(row.stock_quantity)
				for row in products_data
				if row.price and row.stock_quantity
			)
			total_stock = sum(
				int(row.stock_quantity) for row in products_data if row.stock_quantity
			)
			avg_price = (
				sum(float(row.price) for row in products_data if row.price)
				/ total_products
				if total_products
				else 0
			)

			filename, file_path = self._generate_filename("pdf", "products_report")

			doc = SimpleDocTemplate(file_path, pagesize=A4)
			styles = getSampleStyleSheet()
			story = []

			title_style = ParagraphStyle(
				"CustomTitle",
				parent=styles["Heading1"],
				fontSize=18,
				spaceAfter=30,
				alignment=1,
			)
			story.append(Paragraph(report_title, title_style))
			story.append(Spacer(1, 20))

			summary_style = styles["Heading2"]
			story.append(Paragraph("Summary", summary_style))
			story.append(Spacer(1, 10))

			summary_text = f"""
			<b>Total Products:</b> {total_products}<br/>
			<b>Total Inventory Value:</b> ${total_value:,.2f}<br/>
			<b>Total Stock Quantity:</b> {total_stock}<br/>
			<b>Average Product Price:</b> ${avg_price:,.2f}
			"""
			story.append(Paragraph(summary_text, styles["Normal"]))
			story.append(Spacer(1, 20))

			story.append(Paragraph("Product Details", summary_style))
			story.append(Spacer(1, 10))

			table_data = [["Name", "Category", "Price", "Stock", "Description"]]

			for row in products_data[:50]:
				description = (
					(row.description or "N/A")[:30] + "..."
					if row.description and len(row.description) > 30
					else (row.description or "N/A")
				)
				table_data.append(
					[
						row.name or "N/A",
						row.category or "N/A",
						f"${float(row.price):,.2f}" if row.price else "N/A",
						str(row.stock_quantity) if row.stock_quantity else "0",
						description,
					]
				)

			table = Table(table_data)
			table.setStyle(
				TableStyle(
					[
						("BACKGROUND", (0, 0), (-1, 0), colors.grey),
						("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
						("ALIGN", (0, 0), (-1, -1), "CENTER"),
						("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
						("FONTSIZE", (0, 0), (-1, 0), 9),
						("BOTTOMPADDING", (0, 0), (-1, 0), 12),
						("BACKGROUND", (0, 1), (-1, -1), colors.beige),
						("FONTSIZE", (0, 1), (-1, -1), 7),
						("GRID", (0, 0), (-1, -1), 1, colors.black),
					]
				)
			)

			story.append(table)

			if include_sales_data and sales_data:
				story.append(Spacer(1, 20))
				story.append(Paragraph("Sales Performance", summary_style))
				story.append(Spacer(1, 10))

				sales_table_data = [
					[
						"Product",
						"Category",
						"Total Revenue",
						"Qty Sold",
						"Orders",
						"Avg Order",
					]
				]

				for row in sales_data[:25]:
					sales_table_data.append(
						[
							row.product_name or "N/A",
							row.category or "N/A",
							f"${float(row.total_revenue):,.2f}"
							if row.total_revenue
							else "$0.00",
							str(row.total_quantity_sold)
							if row.total_quantity_sold
							else "0",
							str(row.total_orders) if row.total_orders else "0",
							f"${float(row.avg_order_value):,.2f}"
							if row.avg_order_value
							else "$0.00",
						]
					)

				sales_table = Table(sales_table_data)
				sales_table.setStyle(
					TableStyle(
						[
							("BACKGROUND", (0, 0), (-1, 0), colors.grey),
							("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
							("ALIGN", (0, 0), (-1, -1), "CENTER"),
							("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
							("FONTSIZE", (0, 0), (-1, 0), 8),
							("BOTTOMPADDING", (0, 0), (-1, 0), 12),
							("BACKGROUND", (0, 1), (-1, -1), colors.beige),
							("FONTSIZE", (0, 1), (-1, -1), 7),
							("GRID", (0, 0), (-1, -1), 1, colors.black),
						]
					)
				)

				story.append(sales_table)

			doc.build(story)

			return {
				"success": True,
				"message": "Products report exported successfully to PDF",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"record_count": len(products_data),
				"summary": {
					"total_products": total_products,
					"total_inventory_value": total_value,
					"total_stock": total_stock,
					"avg_price": avg_price,
				},
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting products to PDF: {str(e)}",
			}

	async def export_custom_query_to_excel(
		self,
		query_type: str,
		filters: dict[str, Any] | None = None,
		export_format: str = "xlsx",
	) -> dict[str, Any]:
		"""Export custom query results to Excel with multiple sheets."""
		try:
			await self.db.rollback()

			filters = filters or {}

			if query_type == "comprehensive_sales":
				return await self._export_comprehensive_sales_excel(filters)
			elif query_type == "customer_analysis":
				return await self._export_customer_analysis_excel(filters)
			elif query_type == "product_performance":
				return await self._export_product_performance_excel(filters)
			else:
				return {
					"success": False,
					"message": f"Unknown query type: {query_type}",
				}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting custom query: {str(e)}",
			}

	async def _export_comprehensive_sales_excel(
		self, filters: dict[str, Any]
	) -> dict[str, Any]:
		"""Export comprehensive sales analysis to Excel."""
		await self.db.rollback()

		filename, file_path = self._generate_filename("xlsx", "comprehensive_sales")

		with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
			overview_query = (
				select(
					func.date(Sale.sale_date).label("sale_date"),
					func.count(Sale.id).label("total_orders"),
					func.sum(Sale.amount).label("daily_revenue"),
					func.avg(Sale.amount).label("avg_order_value"),
					func.sum(Sale.quantity).label("items_sold"),
				)
				.group_by(func.date(Sale.sale_date))
				.order_by(func.date(Sale.sale_date).desc())
				.limit(90)
			)

			result = await self.db.execute(overview_query)
			overview_data = result.fetchall()

			if overview_data:
				overview_df = pd.DataFrame(
					[dict(row._mapping) for row in overview_data]
				)
				overview_df.to_excel(writer, sheet_name="Daily Overview", index=False)

			products_query = (
				select(
					Sale.product_name.label("name"),
					Sale.category,
					func.sum(Sale.quantity).label("total_sold"),
					func.sum(Sale.amount).label("total_revenue"),
					func.avg(Sale.amount).label("avg_sale_value"),
				)
				.where(Sale.product_id.is_not(None))
				.group_by(Sale.product_id, Sale.product_name, Sale.category)
				.order_by(func.sum(Sale.amount).desc())
				.limit(50)
			)

			result = await self.db.execute(products_query)
			products_data = result.fetchall()

			if products_data:
				products_df = pd.DataFrame(
					[dict(row._mapping) for row in products_data]
				)
				products_df.to_excel(writer, sheet_name="Top Products", index=False)

			customers_query = (
				select(
					Sale.customer_name.label("name"),
					Customer.customer_type,
					func.count(Sale.id).label("total_orders"),
					func.sum(Sale.amount).label("total_spent"),
					func.avg(Sale.amount).label("avg_order_value"),
					func.max(Sale.sale_date).label("last_purchase"),
				)
				.select_from(
					Sale.__table__.join(
						Customer.__table__, Sale.customer_id == Customer.id
					)
				)
				.group_by(Sale.customer_id, Sale.customer_name, Customer.customer_type)
				.order_by(func.sum(Sale.amount).desc())
				.limit(100)
			)

			result = await self.db.execute(customers_query)
			customers_data = result.fetchall()

			if customers_data:
				customers_df = pd.DataFrame(
					[dict(row._mapping) for row in customers_data]
				)
				customers_df.to_excel(
					writer, sheet_name="Customer Analysis", index=False
				)

		return {
			"success": True,
			"message": "Comprehensive sales analysis exported successfully",
			"file_url": f"/static/exports/{filename}",
			"filename": filename,
			"sheets": ["Daily Overview", "Top Products", "Customer Analysis"],
		}

	async def _export_customer_analysis_excel(
		self, filters: dict[str, Any]
	) -> dict[str, Any]:
		"""Export customer analysis to Excel."""
		filename, file_path = self._generate_filename("xlsx", "customer_analysis")

		start_date = filters.get("start_date")
		end_date = filters.get("end_date")

		try:
			await self.db.rollback()
			check_query = select(func.count(Sale.id)).select_from(Sale.__table__)
			if start_date:
				check_query = check_query.where(Sale.sale_date >= start_date)
			if end_date:
				check_query = check_query.where(Sale.sale_date <= end_date)

			result = await self.db.execute(check_query)
			sales_count = result.scalar()

			if not sales_count or sales_count == 0:
				return {
					"success": False,
					"message": f"No sales data found for the specified criteria. Start date: {start_date}, End date: {end_date}",
				}

			with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
				customer_query = select(
					Customer.customer_name.label("name"),
					Customer.email,
					Customer.customer_type,
					Customer.city,
					func.count(Sale.id).label("total_orders"),
					func.sum(Sale.amount).label("total_spent"),
					func.avg(Sale.amount).label("avg_order_value"),
					func.max(Sale.sale_date).label("last_purchase_date"),
				).select_from(
					Customer.__table__.join(
						Sale.__table__, Customer.id == Sale.customer_id
					)
				)

				if start_date:
					customer_query = customer_query.where(Sale.sale_date >= start_date)
				if end_date:
					customer_query = customer_query.where(Sale.sale_date <= end_date)

				customer_query = customer_query.group_by(
					Customer.id,
					Customer.customer_name,
					Customer.email,
					Customer.customer_type,
					Customer.city,
				).order_by(func.sum(Sale.amount).desc())

				result = await self.db.execute(customer_query)
				customer_data = result.fetchall()

				if customer_data:
					customer_df = pd.DataFrame(
						[dict(row._mapping) for row in customer_data]
					)
					customer_df.to_excel(
						writer, sheet_name="Customer Analysis", index=False
					)

				summary_data = {
					"Metric": ["Total Customers", "Total Sales", "Average Order Value"],
					"Value": [
						len(customer_data),
						f"${customer_df['total_spent'].sum():,.2f}"
						if customer_data
						else "$0.00",
						f"${customer_df['avg_order_value'].mean():,.2f}"
						if customer_data
						else "$0.00",
					],
				}
				summary_df = pd.DataFrame(summary_data)
				summary_df.to_excel(writer, sheet_name="Summary", index=False)

			return {
				"success": True,
				"message": "Customer analysis exported successfully",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"sheets": ["Customer Analysis", "Summary"],
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting customer analysis: {str(e)}",
			}

	async def _export_product_performance_excel(
		self, filters: dict[str, Any]
	) -> dict[str, Any]:
		"""Export product performance analysis to Excel."""
		filename, file_path = self._generate_filename("xlsx", "product_performance")

		start_date = filters.get("start_date")
		end_date = filters.get("end_date")
		category = filters.get("category")

		try:
			await self.db.rollback()
			check_query = select(func.count(Sale.id)).select_from(Sale.__table__)
			if start_date:
				check_query = check_query.where(Sale.sale_date >= start_date)
			if end_date:
				check_query = check_query.where(Sale.sale_date <= end_date)

			result = await self.db.execute(check_query)
			sales_count = result.scalar()

			if not sales_count or sales_count == 0:
				return {
					"success": False,
					"message": f"No sales data found for the specified criteria. Start date: {start_date}, End date: {end_date}",
				}

			with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
				product_query = select(
					Product.product_name.label("name"),
					Category.category_name.label("category"),
					Product.unit_price.label("price"),
					Product.stock_quantity,
					func.count(Sale.id).label("total_orders"),
					func.sum(Sale.quantity).label("total_quantity_sold"),
					func.sum(Sale.amount).label("total_revenue"),
					func.avg(Sale.amount).label("avg_order_value"),
					func.max(Sale.sale_date).label("last_sale_date"),
				).select_from(
					Product.__table__.outerjoin(
						Category.__table__, Product.category_id == Category.id
					).outerjoin(Sale.__table__, Product.id == Sale.product_id)
				)

				if start_date:
					product_query = product_query.where(Sale.sale_date >= start_date)
				if end_date:
					product_query = product_query.where(Sale.sale_date <= end_date)
				if category:
					product_query = product_query.where(
						Category.category_name == category
					)

				product_query = product_query.group_by(
					Product.id,
					Product.product_name,
					Category.category_name,
					Product.unit_price,
					Product.stock_quantity,
				).order_by(func.sum(Sale.amount).desc())

				result = await self.db.execute(product_query)
				product_data = result.fetchall()

				if product_data:
					product_df = pd.DataFrame(
						[dict(row._mapping) for row in product_data]
					)
					product_df.to_excel(
						writer, sheet_name="Product Performance", index=False
					)

				summary_data = {
					"Metric": ["Total Products", "Total Revenue", "Average Price"],
					"Value": [
						len(product_data),
						f"${product_df['total_revenue'].sum():,.2f}"
						if product_data
						else "$0.00",
						f"${product_df['price'].mean():,.2f}"
						if product_data
						else "$0.00",
					],
				}
				summary_df = pd.DataFrame(summary_data)
				summary_df.to_excel(writer, sheet_name="Summary", index=False)

			return {
				"success": True,
				"message": "Product performance analysis exported successfully",
				"file_url": f"/static/exports/{filename}",
				"filename": filename,
				"sheets": ["Product Performance", "Summary"],
			}

		except Exception as e:
			return {
				"success": False,
				"message": f"Error exporting product performance: {str(e)}",
			}

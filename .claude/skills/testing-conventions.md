# Testing Conventions for DocuMind

## Philosophy
- Tests are written alongside the feature, not after
- Test the contract (inputs/outputs), not the internals
- Every bug fix includes a regression test

## Backend (pytest)
### Endpoint test pattern:
async def test_upload_document(client, auth_headers):
    response = await client.post(
        "/api/v1/documents/upload",
        headers=auth_headers,
        files={"file": ("test.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert "id" in response.json()["data"]

### What to assert on endpoints:
- Status code
- Response body structure
- Database state changed correctly
- Auth rejection when no token / wrong role

## Frontend (Vitest + RTL)
### Component test pattern:
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { UploadPage } from "./UploadPage"

test("shows error for non-PDF files", async () => {
    render(<UploadPage />)
    const input = screen.getByLabelText(/upload/i)
    await userEvent.upload(input, nonPdfFile)
    expect(screen.getByRole("alert")).toHaveTextContent(/pdf only/i)
})

## When NOT to test
- Pure UI with no logic (a static footer, a logo)
- Third-party library behavior
- Exact CSS values
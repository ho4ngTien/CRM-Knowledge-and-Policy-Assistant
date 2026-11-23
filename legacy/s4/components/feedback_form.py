"""
legacy/s4/components/feedback_form.py
Ghi nhận đánh giá của người dùng (CKPA-46 / KNW 07).
5 nhóm phản hồi hợp lệ, 2 cờ bổ sung, ghi nhận qua feedback_service.
Không nhập thông tin cá nhân khách hàng.
Phong cách: Enterprise Banking — ngôn ngữ vận hành nghiệp vụ ngân hàng.
"""

import streamlit as st
from legacy.s4.services.feedback_service import submit_feedback

# ---------------------------------------------------------------------------
# Mapping nhóm vấn đề — ngôn ngữ vận hành nghiệp vụ ngân hàng (CKPA-46)
# ---------------------------------------------------------------------------
_FEEDBACK_OPTIONS = {
    "Missing Source":    "Thiếu nguồn trích dẫn văn bản",
    "Outdated Rule":     "Văn bản hết hiệu lực / Cần cập nhật",
    "Wrong Scope":       "Chưa phù hợp với phân khúc / sản phẩm",
    "Missing Exception": "Chưa phản ánh trường hợp ngoại lệ chính sách",
    "Refusal":           "Từ chối không phù hợp với nghiệp vụ",
}

_LABEL_TO_CODE = {v: k for k, v in _FEEDBACK_OPTIONS.items()}

# SVG icon nhỏ — tránh emoji trang trí trong tiêu đề form
_SVG_FEEDBACK = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none">'
    '<path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"'
    ' fill="#1F5C99"/></svg>'
)


def render_feedback_form(
    question: str,
    hold_reason_code: str | None = None,
) -> None:
    """
    Hiển thị form đóng góp ý kiến.
    Cho phép feedback kể cả khi câu hỏi bị HOLD.
    """
    with st.expander("Đóng góp ý kiến về câu trả lời (Feedback)", expanded=False):
        if not question or not question.strip():
            st.caption("Hãy nhập câu hỏi trước khi gửi phản hồi.")
            return

        # Tiêu đề section
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:8px;
                           margin-bottom:14px;padding-bottom:12px;
                           border-bottom:1px solid #E2E8F0">
                {_SVG_FEEDBACK}
                <div>
                    <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                                color:#64748B;text-transform:uppercase">
                        Phản hồi nghiệp vụ nội bộ
                    </div>
                    <div style="font-size:0.82rem;color:#1E293B">
                        Thông tin phản hồi phục vụ công tác rà soát và cải tiến hệ thống
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Đánh giá tổng thể
        st.markdown(
            """<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                          color:#64748B;text-transform:uppercase;margin-bottom:6px">
                Đánh giá tổng thể
            </div>""",
            unsafe_allow_html=True,
        )
        helpful = st.radio(
            label="Mức độ hữu ích",
            options=["Hữu ích — Thông tin chính xác, đủ căn cứ",
                     "Chưa hữu ích — Cần xem xét lại"],
            horizontal=True,
            index=0,
            label_visibility="collapsed",
            key=f"helpful_radio_{abs(hash(question))}",
        )

        is_unhelpful = "Chưa hữu ích" in helpful

        form_key = f"feedback_form_{abs(hash(question))}"

        with st.form(key=form_key, clear_on_submit=True):

            if is_unhelpful:
                st.markdown(
                    """<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                                  color:#64748B;text-transform:uppercase;
                                  margin-top:14px;margin-bottom:6px">
                        Nhóm vấn đề phát hiện (Bắt buộc khi Chưa hữu ích)
                    </div>""",
                    unsafe_allow_html=True,
                )
                selected_label = st.radio(
                    label="Chọn nhóm vấn đề",
                    options=list(_FEEDBACK_OPTIONS.values()),
                    index=None,
                    label_visibility="collapsed",
                )
            else:
                selected_label = None

            # Cờ kiểm soát bổ sung — xếp theo chiều dọc (1 cột), nhãn đầy đủ không bị cắt
            st.markdown(
                """<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                              color:#64748B;text-transform:uppercase;
                              margin-top:14px;margin-bottom:8px">
                    Cờ kiểm soát bổ sung
                </div>""",
                unsafe_allow_html=True,
            )
            flag_missing_exc = st.checkbox(
                "Chưa phản ánh ngoại lệ quan trọng",
                help="Đánh dấu nếu câu trả lời bỏ sót một trường hợp ngoại lệ của chính sách.",
            )
            flag_unfounded = st.checkbox(
                "Có khẳng định thiếu căn cứ văn bản",
                help="Đánh dấu nếu câu trả lời đưa ra thông tin không có nguồn gốc rõ ràng.",
            )

            st.markdown(
                """<div style="margin-top:12px;margin-bottom:4px;
                              font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                              color:#64748B;text-transform:uppercase">
                    Ghi chú bổ sung
                </div>
                <div style="font-size:0.76rem;color:#94A3B8;margin-bottom:6px">
                    Không nhập thông tin cá nhân hoặc dữ liệu định danh khách hàng.
                </div>""",
                unsafe_allow_html=True,
            )
            note = st.text_area(
                label="Ghi chú",
                placeholder="Ví dụ: Quyết định sửa đổi số 123/QĐ-... đã thay thế quy định này từ tháng 06/2025.",
                max_chars=500,
                label_visibility="collapsed",
            )

            st.markdown(
                """<div style="margin-top:4px;margin-bottom:12px;
                              font-size:0.74rem;color:#94A3B8;text-align:right">
                    Tối đa 500 ký tự
                </div>""",
                unsafe_allow_html=True,
            )

            submitted = st.form_submit_button(
                "Gửi phản hồi nghiệp vụ",
                use_container_width=True,
                type="primary",
            )

            if submitted:
                if is_unhelpful:
                    if not selected_label:
                        st.error("Vui lòng chọn một nhóm vấn đề khi đánh giá 'Chưa hữu ích'.")
                        return
                    feedback_type = _LABEL_TO_CODE.get(selected_label)
                    is_helpful_bool = False
                else:
                    feedback_type = None
                    is_helpful_bool = True

                ok = submit_feedback(
                    question=question,
                    feedback_type=feedback_type,
                    comment=note.strip(),
                    is_helpful=is_helpful_bool,
                    flag_missing_exception=flag_missing_exc,
                    flag_unfounded_claim=flag_unfounded,
                )

                if ok:
                    st.success(
                        "✅ Đã ghi nhận — Cảm ơn bạn đã đóng góp ý kiến nghiệp vụ. "
                        "Phản hồi sẽ được xem xét trong chu kỳ rà soát hệ thống định kỳ."
                    )
                else:
                    st.error(
                        "Không thể lưu phản hồi. "
                        "Vui lòng thử lại hoặc liên hệ bộ phận kỹ thuật."
                    )

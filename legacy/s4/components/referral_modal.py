"""
legacy/s4/components/referral_modal.py
Chuyển câu hỏi đến người phụ trách chính sách (CKPA-45 / KNW 05).
Quy tắc an toàn:
  - Ghi nhận yêu cầu qua referral_service (CỤC BỘ, KHÔNG gửi email, KHÔNG tạo CRM Task).
  - Hiển thị danh sách referral gần đây để kiểm tra.
  - Thông báo rõ: hệ thống KHÔNG tự gửi cho ai.
Phong cách: Enterprise Banking — văn phong tuân thủ nội bộ.
"""

import streamlit as st
from legacy.s4.services.referral_service import submit_referral, list_recent_referrals

_POLICY_OWNERS = [
    "Phòng Quản lý Sản phẩm & Chính sách Bán lẻ",
    "Khối Quản trị Rủi ro Tín dụng",
    "Phòng Pháp chế & Tuân thủ",
    "Trung tâm Dịch vụ Khách hàng (CRM Ops)",
    "Chưa xác định",
]

_REFERRAL_REASONS = [
    "Câu hỏi vượt ngoài phạm vi tài liệu hiện có",
    "Cần xin ngoại lệ chính sách",
    "Chính sách mâu thuẫn, cần xác nhận từ cấp có thẩm quyền",
    "Trường hợp khách hàng đặc biệt / ưu tiên",
    "Hệ thống trả lời HOLD — cần người có thẩm quyền xử lý",
    "Khác",
]

# SVG icon chuyển tiếp
_SVG_FORWARD = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none">'
    '<path d="M12 4l8 8-8 8M4 12h16" stroke="#1F5C99" stroke-width="2.2"'
    ' stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

_SVG_CLOCK = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="9" stroke="#64748B" stroke-width="2"/>'
    '<path d="M12 7v5l3 3" stroke="#64748B" stroke-width="2"'
    ' stroke-linecap="round" stroke-linejoin="round"/></svg>'
)

_SVG_LOCK = (
    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none">'
    '<rect x="5" y="11" width="14" height="10" rx="2" stroke="#64748B" stroke-width="2"/>'
    '<path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#64748B" stroke-width="2"'
    ' stroke-linecap="round"/></svg>'
)


def render_referral_form(
    question: str,
    default_policy_owner: str = "Chưa xác định",
) -> None:
    """
    Hiển thị form chuyển câu hỏi đến người phụ trách chính sách.
    Chỉ lưu cục bộ qua referral_service — không gửi email hay tạo CRM task.
    """
    with st.expander("Chuyển tuyến đến Đơn vị phụ trách chính sách (Referral)", expanded=False):

        # Tiêu đề section
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:8px;
                           margin-bottom:12px;padding-bottom:12px;
                           border-bottom:1px solid #E2E8F0">
                {_SVG_FORWARD}
                <div>
                    <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                                color:#64748B;text-transform:uppercase">
                        Yêu cầu chuyển tuyến chính sách
                    </div>
                    <div style="font-size:0.82rem;color:#1E293B">
                        Sử dụng khi câu hỏi phức tạp, nằm ngoài tài liệu hiện có
                        hoặc hệ thống đang ở trạng thái HOLD
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Lưu ý nghiệp vụ — văn phong tuân thủ nội bộ
        st.markdown(
            f"""<div style="background:#EFF6FF;border:1px solid #BFDBFE;
                           border-left:4px solid #1F5C99;border-radius:0 8px 8px 0;
                           padding:12px 16px;margin-bottom:16px">
                <div style="font-size:0.72rem;font-weight:800;letter-spacing:0.1em;
                            color:#1D4ED8;text-transform:uppercase;margin-bottom:5px;
                            display:flex;align-items:center;gap:5px">
                    {_SVG_LOCK}
                    <span>Lưu ý nghiệp vụ</span>
                </div>
                <div style="font-size:0.85rem;color:#1E3A5F;line-height:1.65">
                    Dữ liệu được ghi nhận vào hệ thống nội bộ để phục vụ công tác rà soát.
                    Vui lòng thực hiện thủ tục chuyển tuyến chính sách theo quy trình đơn vị.
                    <strong>Hệ thống không tự gửi thông báo cho bất kỳ cá nhân hay bộ phận nào.</strong>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

        form_key = f"referral_form_{abs(hash(question))}"

        with st.form(key=form_key, clear_on_submit=True):

            st.markdown(
                """<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                              color:#64748B;text-transform:uppercase;margin-bottom:6px">
                    Lý do chuyển tuyến
                </div>""",
                unsafe_allow_html=True,
            )
            reason_choice = st.selectbox(
                label="Lý do",
                options=_REFERRAL_REASONS,
                index=0,
                label_visibility="collapsed",
            )

            st.markdown(
                """<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                              color:#64748B;text-transform:uppercase;
                              margin-top:14px;margin-bottom:4px">
                    Ghi chú bổ sung
                </div>
                <div style="font-size:0.76rem;color:#94A3B8;margin-bottom:6px">
                    Không nhập thông tin cá nhân hoặc dữ liệu định danh khách hàng.
                </div>""",
                unsafe_allow_html=True,
            )
            reason_note = st.text_area(
                label="Ghi chú",
                placeholder="Mô tả thêm tình huống, yêu cầu cụ thể hoặc số hiệu văn bản liên quan...",
                max_chars=500,
                label_visibility="collapsed",
            )

            st.markdown(
                """<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                              color:#64748B;text-transform:uppercase;
                              margin-top:14px;margin-bottom:6px">
                    Đơn vị phụ trách tiếp nhận
                </div>""",
                unsafe_allow_html=True,
            )
            default_idx = 0
            if default_policy_owner in _POLICY_OWNERS:
                default_idx = _POLICY_OWNERS.index(default_policy_owner)
            policy_owner = st.selectbox(
                label="Đơn vị tiếp nhận",
                options=_POLICY_OWNERS,
                index=default_idx,
                label_visibility="collapsed",
            )

            submitted = st.form_submit_button(
                "Lưu yêu cầu chuyển tuyến vào hệ thống",
                use_container_width=True,
                type="primary",
            )

            if submitted:
                full_reason = reason_choice
                if reason_note.strip():
                    full_reason = f"{reason_choice}: {reason_note.strip()}"

                ok = submit_referral(
                    question=question,
                    reason=full_reason,
                    policy_owner=policy_owner,
                    status="Mới tạo",
                )

                if ok:
                    st.success(
                        f"✅ Đã ghi nhận vào hệ thống nội bộ — Đơn vị tiếp nhận: **{policy_owner}**\n\n"
                        "Lưu ý nghiệp vụ: Dữ liệu được ghi nhận vào hệ thống nội bộ để phục vụ "
                        "công tác rà soát. Vui lòng thực hiện thủ tục chuyển tuyến chính sách "
                        "theo quy trình đơn vị."
                    )
                else:
                    st.error(
                        "Không thể ghi nhận yêu cầu. Vui lòng thử lại hoặc liên hệ bộ phận kỹ thuật."
                    )

        # Lịch sử chuyển tuyến gần đây
        with st.expander("Lịch sử yêu cầu chuyển tuyến gần đây", expanded=False):
            st.markdown(
                f"""<div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                              color:#64748B;text-transform:uppercase;margin-bottom:8px;
                              display:flex;align-items:center;gap:5px">
                    {_SVG_CLOCK} <span>5 yêu cầu gần nhất</span>
                </div>""",
                unsafe_allow_html=True,
            )
            referrals = list_recent_referrals(limit=5)
            if not referrals:
                st.markdown(
                    """<div style="font-size:0.82rem;color:#94A3B8;font-style:italic;
                                  padding:8px 0">
                        Chưa có yêu cầu chuyển tuyến nào được ghi nhận.
                    </div>""",
                    unsafe_allow_html=True,
                )
            else:
                for r in referrals:
                    status_color = "#166534" if r["status"] == "Hoàn thành" else "#92400E"
                    status_bg = "#F0FDF4" if r["status"] == "Hoàn thành" else "#FFFBEB"
                    st.markdown(
                        f"""<div style="border:1px solid #E2E8F0;border-radius:8px;
                                      padding:10px 14px;margin-bottom:8px;background:#F8FAFC">
                            <div style="display:flex;justify-content:space-between;
                                        align-items:center;margin-bottom:4px">
                                <div style="font-size:0.78rem;font-weight:600;color:#1E293B">
                                    {r['created_at'][:16].replace('T', ' &nbsp;')}
                                    &nbsp;—&nbsp;
                                    <span style="color:#1F5C99">{r['policy_owner']}</span>
                                </div>
                                <div style="background:{status_bg};color:{status_color};
                                            border-radius:20px;padding:2px 10px;
                                            font-size:0.7rem;font-weight:700">
                                    {r['status']}
                                </div>
                            </div>
                            <div style="font-size:0.78rem;color:#64748B;line-height:1.5">
                                {r['reason'][:90]}{'...' if len(r['reason']) > 90 else ''}
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

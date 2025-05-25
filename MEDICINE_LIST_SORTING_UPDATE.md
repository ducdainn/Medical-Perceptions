# Cập nhật tính năng sắp xếp cho trang Danh sách thuốc

## Tổng quan
Đã cập nhật trang `/pharmacy/medicines/` với tính năng sắp xếp mới theo yêu cầu:
- 2 dropdown riêng biệt cho tiêu chí sắp xếp và thứ tự
- Sắp xếp theo ngày tạo và số lượng tồn kho
- Tự động cập nhật khi thay đổi lựa chọn (không refresh trang)

## Thay đổi Backend (pharmacy/views.py)

### Medicine List View
```python
@medicine_view_only
def medicine_list(request):
    # Get query parameters
    sort_by = request.GET.get('sort', 'created_at')  # Default sort by created date
    order_by = request.GET.get('order', 'desc')  # Default order desc
    
    # Start with all medicines with inventory prefetch
    medicines = Medicine.objects.select_related().prefetch_related('inventory_set').all()
    
    # Add quantity annotation from first inventory record
    inventory_subquery = Inventory.objects.filter(medicine=OuterRef('pk')).values('quantity')[:1]
    medicines = medicines.annotate(
        inventory_quantity=Subquery(inventory_subquery)
    )
    
    # Handle sorting
    if sort_by == 'created_at':
        if order_by == 'asc':
            medicines = medicines.order_by('created_at')
        else:
            medicines = medicines.order_by('-created_at')
    elif sort_by == 'quantity':
        if order_by == 'asc':
            medicines = medicines.order_by('inventory_quantity', 'name')
        else:
            medicines = medicines.order_by('-inventory_quantity', 'name')
    else:
        # Default to created_at desc
        medicines = medicines.order_by('-created_at')
    
    context = {
        'medicines': medicines,
        'title': 'Danh sách thuốc',
        'sort_by': sort_by,
        'order_by': order_by,
    }
    
    return render(request, 'pharmacy/medicine_list.html', context)
```

**Tính năng mới:**
- Annotation để lấy số lượng tồn kho từ bảng Inventory
- Sắp xếp theo `created_at` (ngày tạo) và `quantity` (số lượng)
- Hỗ trợ cả thứ tự tăng dần (asc) và giảm dần (desc)

## Thay đổi Frontend (pharmacy/templates/pharmacy/medicine_list.html)

### 1. Filter Controls
Thay thế dropdown menu cũ bằng 2 select box riêng biệt:

```html
<div class="col-md-4">
    <select id="sortSelect" class="form-select">
        <option value="created_at" {% if sort_by == 'created_at' %}selected{% endif %}>Ngày tạo</option>
        <option value="quantity" {% if sort_by == 'quantity' %}selected{% endif %}>Số lượng tồn kho</option>
    </select>
</div>
<div class="col-md-4">
    <select id="orderSelect" class="form-select">
        <option value="desc" {% if order_by == 'desc' %}selected{% endif %}>Giảm dần</option>
        <option value="asc" {% if order_by == 'asc' %}selected{% endif %}>Tăng dần</option>
    </select>
</div>
```

### 2. Data Attributes
Thêm data attributes cho JavaScript sorting:

```html
<tr class="medicine-row" 
    data-name="{{ medicine.name|lower }}" 
    data-description="{{ medicine.description|lower }}" 
    data-price="{{ medicine.price }}"
    data-created-at="{{ medicine.created_at|date:'Y-m-d H:i:s' }}"
    data-quantity="{% with inventory=medicine.inventory_set.first %}{% if inventory %}{{ inventory.quantity }}{% else %}0{% endif %}{% endwith %}">
```

### 3. JavaScript Auto-Update
Thêm tính năng auto-update với AJAX:

```javascript
// Auto-update function - sends AJAX request to update the page
function autoUpdate() {
    const sortBy = sortSelect.value;
    const orderBy = orderSelect.value;
    
    const url = new URL(window.location);
    url.searchParams.set('sort', sortBy);
    url.searchParams.set('order', orderBy);
    
    // Update URL without refresh
    window.history.pushState({}, '', url);
    
    // Send AJAX request to get updated content
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Extract the table body content
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTableBody = doc.getElementById('medicineTableBody');
        
        if (newTableBody) {
            medicineTableBody.innerHTML = newTableBody.innerHTML;
            // Update medicineRows array
            medicineRows = Array.from(document.querySelectorAll('.medicine-row'));
        }
    })
    .catch(error => {
        console.error('Error updating data:', error);
        // Fallback to client-side sorting
        clientSideSort(sortBy, orderBy);
    });
}
```

**Tính năng JavaScript:**
- Auto-update với AJAX khi thay đổi dropdown
- Fallback client-side sorting nếu AJAX thất bại
- Hỗ trợ sắp xếp theo ngày tạo và số lượng tồn kho
- Cập nhật URL mà không refresh trang

## Kết quả

✅ **2 dropdown riêng biệt:** Một cho tiêu chí sắp xếp, một cho thứ tự  
✅ **Sắp xếp theo ngày tạo:** Mặc định giảm dần (mới nhất trước)  
✅ **Sắp xếp theo số lượng:** Tăng dần hoặc giảm dần  
✅ **Tự động cập nhật:** Không cần refresh trang khi thay đổi  
✅ **Fallback:** Client-side sorting nếu server không phản hồi  

## Test
- Truy cập: http://localhost:8000/pharmacy/medicines/
- Thử thay đổi các dropdown để kiểm tra tính năng sắp xếp
- Kiểm tra URL được cập nhật tự động
- Verify không có page refresh khi thay đổi 